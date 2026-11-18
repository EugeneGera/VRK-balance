import json
import os
from datetime import datetime, timezone
import uuid

from fastmcp import Client
from agent_server.contracts import AgentError
from agent_server.model import LocalModel
from agent_server.reports import CORE_METRICS, presentation, template_text, verified_facts

DATA_TOOLS = {'get_balance_summary', 'get_balance_details', 'compare_periods'}
CLARIFY = 'ask_clarification'

ALLOWED = {'get_data_catalog','get_filter_values','get_balance_summary','get_balance_details','compare_periods'}
INSTRUCTIONS = """Ты аналитик производственного баланса. Отвечай по-русски.
Для отчёта сначала вызови подходящий инструмент данных. Заголовки и числа отчёта будут построены приложением из его ответа.
Явные даты и фильтры задания имеют приоритет над значениями из интерфейса. Используй фильтры интерфейса для параметров, которые задание не меняет.
Для сравнения нужны два периода. Если нужный параметр нельзя определить из задания, ответа на уточнение и контекста, вызови ask_clarification с одним конкретным вопросом.
Не заменяй запрошенный период другим и не угадывай отсутствующие параметры сравнения. Если пользователь уже ответил на вопрос, используй его ответ.
При запросе разбивки по заводам или площадкам группируй по basis. Периоды задаются явно, месяцы от 1 до 12, каждый диапазон внутри одного года.
Используй идентификаторы показателей из каталога. Не смешивай группы с разными единицами. Считай данные инструментов источником чисел.
История помогает понять задачу, но не является источником показателей. После получения данных закончи вызовы.""".strip()

CLARIFICATION_TOOL = dict(
    type='function', function=dict(
        name=CLARIFY,
        description='Задать аналитику один вопрос о недостающем параметре задания и дождаться ответа.',
        parameters=dict(type='object', properties={'question': {'type': 'string'}},
                        required=['question'], additionalProperties=False),
    ),
)


def clarification_question(text):
    """Accept a standalone natural-language question from models without a tool call."""
    if not isinstance(text, str):
        return None
    lines = text.strip().splitlines()
    if lines:
        question = lines[-1].strip()
        if 0 < len(question) <= 800 and question.endswith('?') and text.count('?') == 1:
            return question
    return None


class Analyst:
    def __init__(self, mcp_url=None, model=None, client_factory=None):
        self.mcp_url = mcp_url or os.environ.get('BALANCE_MCP_URL','http://127.0.0.1:8001/mcp')
        self.model = model or LocalModel()
        self.experiment_digest = os.environ.get('BALANCE_EXPERIMENT_DIGEST') or None
        self.client_factory = client_factory or (lambda token: Client(self.mcp_url,auth=token,timeout=40))

    async def filters(self, token):
        async with self.client_factory(token) as client:
            return await self.call(client,'get_filter_values',{},[])

    async def call(self, client, name, arguments, sources):
        if name not in ALLOWED:
            raise AgentError('unsupported_tool','Запрошен неподдерживаемый инструмент.',400)
        if len(sources) >= 12:
            raise AgentError('tool_limit','Достигнут лимит обращений к данным. Уточните запрос.',422)
        result = await client.call_tool(name,arguments,raise_on_error=False)
        if result.is_error:
            for content in result.content:
                try:
                    error=json.loads(getattr(content,'text',''))
                    raise AgentError(error.get('code','data_error'),error.get('message','Не удалось получить данные.'),
                                     403 if error.get('code') in ('forbidden_filter','insufficient_scope') else 422,error.get('query_id'))
                except (ValueError,TypeError,AttributeError):
                    continue
            raise AgentError('data_error','Не удалось получить данные через MCP.',502)
        payload = result.structured_content
        if not isinstance(payload,dict) or payload.get('status') not in ('ok','empty') or 'data' not in payload or 'metadata' not in payload:
            raise AgentError('invalid_data_response','MCP вернул неполный ответ.',502)
        sources.append(dict(tool=name,arguments=arguments,response=payload))
        return payload

    async def run(self, request, token, audit=None):
        audit = audit if audit is not None else {}
        audit['attempt_id'] = str(request.attempt_id or uuid.uuid4())
        audit['model_requested'] = self.model.name
        audit['profile'] = 'experiment' if self.experiment_digest else 'local'
        audit['tools'] = []
        audit['agent_tools'] = []
        if request.action == 'chat' and not request.message:
            raise AgentError('empty_message', 'Введите задание или ответ.', 400)
        if request.action == 'comparison' and request.baseline is None:
            raise AgentError('baseline_required', 'Выберите базовый период для сравнения.', 400)

        status = await self.model.status()
        compact = status['model'] == 'qwen3:0.6b'
        is_chat = request.action == 'chat'
        attempted_mode = ('compact' if compact else 'agent') if is_chat else 'preset'
        audit.update(attempted_mode=attempted_mode, model=None, model_digest=status.get('digest'),
                     model_settings=status.get('settings'), execution_mode=None, fallback_reason=None)
        if self.experiment_digest and (not status['ready'] or status.get('digest') != self.experiment_digest):
            raise AgentError('experiment_model_mismatch', 'Зафиксированная модель эксперимента недоступна.', 503)
        if is_chat and not status['ready']:
            raise AgentError('model_unavailable', 'Подготовка ответов недоступна. Проверьте запуск приложения.')
        if compact and is_chat and request.baseline is None and 'сравн' in request.message.lower():
            raise AgentError('comparison_needs_filters', 'Выберите «Сравнение» и задайте базовый период.', 400)

        sources = []

        async def get_data(client, name, arguments, *, selected_by_model=False):
            if name not in ALLOWED:
                raise AgentError('unsupported_tool', 'Запрошен неподдерживаемый инструмент.', 400)
            audit['tools'].append(name)
            if selected_by_model:
                audit['agent_tools'].append(name)
            payload = await self.call(client, name, arguments, sources)
            metadata = payload['metadata']
            if metadata.get('query_id'):
                audit.setdefault('source_query_ids', []).append(metadata['query_id'])
            if metadata.get('actor'):
                audit['actor'] = metadata['actor']
            return payload

        async with self.client_factory(token) as client:
            catalog = (await get_data(client, 'get_data_catalog', {}))['data']
            question = (request.task + ' ' + request.message).strip().lower()
            breakdown = request.action == 'details' or (compact and is_chat and
                any(word in question for word in ('базис', 'завод', 'комплекс')))
            if attempted_mode == 'agent':
                audit['model'] = status['model']
                ask = await self.converse(client, request, catalog, sources, get_data)
                if ask:
                    audit['execution_mode'] = 'agent'
                    return self.response(request, audit, 'clarification', ask, [], [])
            else:
                arguments = request.context.arguments()
                arguments['metrics'] = CORE_METRICS
                if breakdown:
                    arguments.update(group_by=['basis'], limit=200)
                    await get_data(client, 'get_balance_details', arguments)
                elif request.baseline is not None and request.action in ('comparison', 'chat'):
                    arguments['comparison'] = arguments.pop('period')
                    arguments['baseline'] = request.baseline.model_dump(exclude_none=True)
                    await get_data(client, 'compare_periods', arguments)
                else:
                    await get_data(client, 'get_balance_summary', arguments)

            tables, provenance = presentation(sources, catalog)
            source_tool = next(source['tool'] for source in sources if source['tool'] in DATA_TOOLS)
            template_action = {'compare_periods': 'comparison', 'get_balance_details': 'details'}.get(source_tool, 'summary')
            text = template_text(template_action, sources)
            facts, primary = verified_facts(tables)
            audit['execution_mode'] = 'template'
            if not facts:
                audit['fallback_reason'] = 'empty_data'
            elif not status['ready']:
                audit['fallback_reason'] = status.get('reason') or 'model_unavailable'
            else:
                audit['model'] = status['model']
                prompt = request.message or {'summary': 'Главные показатели периода.',
                    'comparison': 'Основные изменения двух периодов.', 'details': 'Распределение по базисам.'}[request.action]
                if request.task and request.task != request.message:
                    prompt = f'Исходное задание: {request.task}\nПоследнее сообщение: {prompt}'
                limit = min(len(facts), 1 if any(word in question for word in ('кратко', 'короче', 'кратче')) else 4)
                try:
                    chosen = await self.model.select_facts(facts[:200], prompt, limit)
                    if not chosen:
                        raise AgentError('invalid_model_evidence', 'Модель не выбрала показатели.', 502)
                except AgentError as error:
                    audit['fallback_reason'] = error.code
                else:
                    ids = list(dict.fromkeys((primary if breakdown or not is_chat else []) + chosen))
                    text = '\n\n'.join(facts[item]['text'] for item in ids[:8])
                    audit['execution_mode'] = attempted_mode
            return self.response(request, audit, 'report', text, tables, provenance)

    @staticmethod
    def response(request, audit, kind, text, tables, provenance):
        mode = 'template' if audit['execution_mode'] == 'template' else 'local_model'
        return dict(id=str(uuid.uuid4()), kind=kind, mode=mode, text=text, tables=tables, sources=provenance,
                    context=request.context.model_dump(), created_at=datetime.now(timezone.utc).isoformat(),
                    empty=kind == 'report' and not tables, **audit)

    async def converse(self, client, request, catalog, sources, get_data):
        discovered = await client.list_tools()
        tools = [
            dict(type='function', function=dict(name=tool.name, description=tool.description, parameters=tool.input_schema))
            for tool in discovered if tool.name in ALLOWED and tool.annotations and tool.annotations.read_only_hint
        ]
        if {tool['function']['name'] for tool in tools} != ALLOWED:
            raise AgentError('tool_catalog_changed', 'Набор разрешённых MCP-инструментов изменился.', 502)
        tools.append(CLARIFICATION_TOOL)
        messages = [dict(role='system', content=INSTRUCTIONS)]
        messages.extend(dict(role=item.role, content=item.content[:1600]) for item in request.history[-6:])
        messages.append(dict(role='user', content=json.dumps(dict(
            context=request.context.model_dump(),
            baseline=request.baseline.model_dump() if request.baseline else None,
            task=request.task or request.message,
            latest_message=request.message,
            metrics={key: value['name'] for key, value in catalog['metrics'].items()},
        ), ensure_ascii=False)))

        defaults = request.context.arguments()
        for _ in range(5):
            message = await self.model.reply(messages, tools)
            calls = message.get('tool_calls') or []
            if not calls:
                ask = clarification_question(message.get('content'))
                if ask:
                    return ask
                if any(source['tool'] in DATA_TOOLS for source in sources):
                    return None
                raise AgentError('no_report_data', 'Для задания не получены данные. Уточните показатели и период.', 422)
            if not isinstance(calls, list) or len(calls) > 5:
                raise AgentError('invalid_tool_call', 'Модель запросила слишком много инструментов.', 422)
            messages.append(message)
            for call in calls:
                try:
                    name = call['function']['name']
                    arguments = call['function']['arguments']
                    arguments = json.loads(arguments) if isinstance(arguments, str) else arguments
                    if not isinstance(arguments, dict):
                        raise ValueError()
                except (ValueError, KeyError, TypeError):
                    raise AgentError('invalid_tool_call', 'Модель вернула некорректный запрос данных.', 422)
                if name == CLARIFY:
                    question = arguments.get('question')
                    if isinstance(question, str) and 0 < len(question.strip()) <= 800:
                        return question.strip()
                    raise AgentError('invalid_clarification', 'Модель не сформулировала уточняющий вопрос.', 502)
                if name in DATA_TOOLS:
                    for key in ('products', 'categories', 'basises'):
                        if key in defaults:
                            arguments.setdefault(key, defaults[key])
                    if name == 'compare_periods':
                        arguments.setdefault('comparison', defaults['period'])
                        if request.baseline:
                            arguments.setdefault('baseline', request.baseline.model_dump(exclude_none=True))
                    else:
                        arguments.setdefault('period', defaults['period'])
                payload = await get_data(client, name, arguments, selected_by_model=True)
                messages.append(dict(role='tool', tool_name=name, content=json.dumps(payload, ensure_ascii=False)))
        raise AgentError('tool_limit', 'Модель не завершила анализ за отведённое число шагов. Уточните задание.', 422)
