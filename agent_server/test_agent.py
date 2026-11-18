import copy
import json
from types import SimpleNamespace
import unittest

import httpx
from starlette.testclient import TestClient

from agent_server.contracts import AgentError,ChatRequest
from agent_server.engine import ALLOWED,Analyst
from agent_server.model import LocalModel
from agent_server.server import create_app


def fixture(tool,arguments):
    period=arguments.get('period') or arguments.get('comparison') or dict(year=2025,month_start=11,month_end=11)
    metadata=dict(query_id='query-'+tool,period=period,applied_filters=dict(products=[dict(id=1,name='АИ-92')],
        categories=[dict(id=101,name='Бензин')],basises=[dict(id=1,name='Север')]),
        data_version=dict(snapshot_id='sha256:fixed'),warnings=[])
    metric=dict(name='Распределённый объём',unit='volume')
    if tool=='get_data_catalog': data=dict(metrics=dict(allocated_volume=metric))
    elif tool=='get_filter_values': data=dict(products=[dict(id=1,name='АИ-92')],categories=[],basises=[],periods=[])
    elif tool=='compare_periods':
        baseline=copy.deepcopy(metadata);baseline['period']=arguments['baseline']
        metadata=dict(query_id='compare-query',baseline=baseline,comparison=metadata,data_version=dict(snapshot_id='sha256:compare'))
        data=dict(groups=[dict(unit=dict(id=2,name='тыс. т'),metrics=dict(allocated_volume=dict(baseline=657,comparison=734,
            absolute_change=77,percent_change=77/657*100,null_reason=None)))])
    else:
        group=dict(unit=dict(id=2,name='тыс. т'),metrics=dict(allocated_volume=657),dimensions={})
        if tool=='get_balance_details':group['dimensions']=dict(basis=dict(id=1,name='Север'))
        data={('rows' if tool=='get_balance_details' else 'groups'):[group]}
    return dict(status='ok',metadata=metadata,data=data)


class FakeMCP:
    def __init__(self): self.calls=[];self.error=False
    async def __aenter__(self): return self
    async def __aexit__(self,*args): pass
    async def call_tool(self,name,arguments,raise_on_error=False):
        self.calls.append((name,arguments))
        if self.error:
            return SimpleNamespace(is_error=True,structured_content=None,
                content=[SimpleNamespace(text=json.dumps(dict(code='forbidden_filter',message='Нет доступа.',query_id='denied-query')))])
        return SimpleNamespace(is_error=False,structured_content=fixture(name,arguments))
    async def list_tools(self):
        return [SimpleNamespace(name=name,description=name,input_schema=dict(type='object'),
            annotations=SimpleNamespace(read_only_hint=True)) for name in ALLOWED]


class FakeModel:
    name='test-local-model'
    def __init__(self,ready=False,messages=None):self.ready=ready;self.messages=list(messages or []);self.requests=[]
    async def status(self):return dict(ready=self.ready,model=self.name,local=True,templates_available=True)
    async def reply(self,messages,tools):
        self.requests.append(copy.deepcopy(messages))
        return self.messages.pop(0)

    async def select_facts(self, facts, question, limit):
        self.requests.append(copy.deepcopy(facts))
        return [fact['id'] for fact in facts[:limit]]


def chat_request(**changes):
    body=dict(action='summary',context=dict(period=dict(year=2025,month_start=11),categories=['Бензин']))
    body.update(changes)
    return ChatRequest.model_validate(body)


class AnalystTests(unittest.IsolatedAsyncioTestCase):
    def make(self,model=None):
        self.mcp=FakeMCP();self.tokens=[]
        def factory(token):self.tokens.append(token);return self.mcp
        return Analyst(model=model or FakeModel(),client_factory=factory)

    async def test_template_works_when_model_is_not_installed(self):
        result=await self.make().run(chat_request(),'caller-token')
        self.assertEqual(result['mode'],'template')
        self.assertEqual(result['tables'][0]['rows'][0]['value'],657)
        self.assertEqual(self.tokens,['caller-token'])
        self.assertEqual(result['sources'][0]['query_id'],'query-get_balance_summary')
        self.assertIn('category_product=',result['sources'][0]['links'][0]['url'])

    async def test_comparison_keeps_backend_differences_and_periods(self):
        result=await self.make().run(chat_request(action='comparison',baseline=dict(year=2025,month_start=10)),'caller')
        row=result['tables'][0]['rows'][0]
        self.assertEqual(row['absolute_change'],77)
        self.assertEqual(result['sources'][0]['baseline']['month_start'],10)
        self.assertEqual(result['tables'][0]['kind'],'comparison')

    async def test_chat_without_model_is_explicitly_unavailable(self):
        with self.assertRaises(AgentError) as caught:
            await self.make().run(chat_request(action='chat',message='Поясни результат'),'caller')
        self.assertEqual(caught.exception.code,'model_unavailable')

    async def test_model_tool_loop_adds_actual_sources_and_keeps_context(self):
        model=FakeModel(True,[dict(role='assistant',content='',tool_calls=[dict(function=dict(name='get_balance_details',
            arguments=dict(period=dict(year=2025,month_start=11),group_by=['basis'])))]),
            dict(role='assistant',content='Распределено 657 тыс. т.')])
        analyst=self.make(model)
        result=await analyst.run(chat_request(action='chat',message='Разбей по базисам'),'limited-caller')
        self.assertEqual(result['mode'],'local_model')
        self.assertEqual(len(result['sources']),2)
        self.assertEqual(result['tables'][1]['title'],'Север')
        self.assertEqual(model.requests[1][-1]['role'],'tool')
        self.assertEqual(self.tokens,['limited-caller'])

    async def test_unlisted_tool_is_never_executed(self):
        model=FakeModel(True,[dict(role='assistant',tool_calls=[dict(function=dict(name='execute_sql',arguments=dict(sql='DROP TABLE x')))])])
        analyst=self.make(model)
        with self.assertRaises(AgentError) as caught:
            await analyst.run(chat_request(action='chat',message='Измени данные'),'caller')
        self.assertEqual(caught.exception.code,'unsupported_tool')
        self.assertNotIn('execute_sql',[name for name,_ in self.mcp.calls])

    async def test_preset_uses_its_prefetched_data_without_offering_extra_tools(self):
        model=FakeModel(True,[dict(role='assistant',content='Распределено 657 тыс. т.')])
        analyst=self.make(model)
        result=await analyst.run(chat_request(),'caller')
        self.assertEqual(result['mode'],'local_model')
        self.assertEqual([name for name,_ in self.mcp.calls],['get_data_catalog','get_balance_summary'])
        self.assertIn('657',model.requests[0][0]['text'])

    async def test_data_failure_is_not_an_empty_report(self):
        analyst=self.make();self.mcp.error=True
        with self.assertRaises(AgentError) as caught:
            await analyst.run(chat_request(),'caller')
        self.assertEqual(caught.exception.status,403)
        self.assertEqual(caught.exception.query_id,'denied-query')

    async def test_selected_filters_are_explicit_on_every_request(self):
        analyst=self.make()
        await analyst.run(chat_request(),'caller')
        await analyst.run(chat_request(context=dict(period=dict(year=2025,month_start=12),products=['АИ-95'])),'caller')
        calls=[args for name,args in self.mcp.calls if name=='get_balance_summary']
        self.assertEqual(calls[0]['categories'],['Бензин'])
        self.assertNotIn('categories',calls[1])
        self.assertEqual(calls[1]['products'],['АИ-95'])


class HTTPContractTests(unittest.TestCase):
    def setUp(self):
        self.mcp=FakeMCP()
        self.client=TestClient(create_app(Analyst(model=FakeModel(),client_factory=lambda token:self.mcp)))

    def test_anonymous_requests_are_denied(self):
        response=self.client.post('/chat',json={})
        self.assertEqual(response.status_code,401)
        self.assertEqual(self.mcp.calls,[])

    def test_invalid_input_is_rejected(self):
        response=self.client.post('/chat',json=dict(action='summary',context=dict(period=dict(year=2025,month_start=13))),headers={'Authorization':'Bearer caller'})
        self.assertEqual(response.status_code,400)
        self.assertEqual(response.json()['error']['code'],'invalid_request')

    def test_comparison_needs_explicit_baseline(self):
        response=self.client.post('/chat',json=chat_request(action='comparison').model_dump(),headers={'Authorization':'Bearer caller'})
        self.assertEqual(response.status_code,400)
        self.assertEqual(response.json()['error']['code'],'baseline_required')

    def test_oversized_body_is_rejected_before_data_access(self):
        response=self.client.post('/chat',content=b'x'*100001,headers={'Authorization':'Bearer caller'})
        self.assertEqual(response.status_code,413)
        self.assertEqual(self.mcp.calls,[])


class ModelTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_requests_only_use_local_native_ollama_protocol(self):
        requests=[]
        def respond(request):
            requests.append(request)
            if request.url.path=='/api/tags':return httpx.Response(200,json=dict(models=[dict(name='qwen3.5:4b-q4_K_M')]))
            return httpx.Response(200,json=dict(message=dict(role='assistant',content='Ответ',thinking='hidden')))
        model=LocalModel(url='http://127.0.0.1:11434',name='qwen3.5:4b-q4_K_M',transport=httpx.MockTransport(respond))
        self.assertTrue((await model.status())['ready'])
        reply=await model.reply([dict(role='user',content='Вопрос')],[])
        self.assertNotIn('thinking',reply)
        body=json.loads(requests[1].content)
        self.assertFalse(body['think'])
        self.assertFalse(body['stream'])
        self.assertEqual(requests[1].url.host,'127.0.0.1')
        self.assertNotIn('authorization',requests[1].headers)

    async def test_missing_model_and_unavailable_runtime_are_distinct(self):
        model=LocalModel(transport=httpx.MockTransport(lambda request:httpx.Response(200,json=dict(models=[]))))
        self.assertEqual((await model.status())['reason'],'model_not_installed')
        model=LocalModel(transport=httpx.MockTransport(lambda request:httpx.Response(503)))
        self.assertEqual((await model.status())['reason'],'ollama_unavailable')

    async def test_cloud_model_cannot_be_enabled_by_accident(self):
        with self.assertRaises(ValueError):LocalModel(name='qwen:cloud')


if __name__=='__main__':unittest.main()
