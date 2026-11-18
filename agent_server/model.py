import json
import os
from urllib.parse import urlsplit

import httpx
from agent_server.contracts import AgentError


class LocalModel:
    def __init__(self, url=None, name=None, transport=None):
        self.url = (url or os.environ.get('BALANCE_OLLAMA_URL', 'http://127.0.0.1:11434')).rstrip('/')
        self.name = name or os.environ.get('BALANCE_OLLAMA_MODEL', 'qwen3.5:4b-q4_K_M')
        parsed = urlsplit(self.url)
        if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('BALANCE_OLLAMA_URL must be a service URL without credentials or query')
        if ':cloud' in self.name.lower() or '/' in self.name:
            raise ValueError('Choose an installed local Ollama model, not a cloud model')
        self.transport = transport

    async def status(self):
        ready, reason = False, 'ollama_unavailable'
        try:
            async with httpx.AsyncClient(timeout=3, trust_env=False, transport=self.transport) as client:
                response = await client.get(self.url+'/api/tags')
                response.raise_for_status()
                models = response.json()['models']
            installed = next((item for item in models if item.get('name') == self.name or item.get('model') == self.name),None)
            ready = installed is not None
            reason = None if ready else 'model_not_installed'
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            pass
        return dict(ready=ready, reason=reason, provider='ollama', model=self.name, local=True, templates_available=True)

    async def reply(self, messages, tools, format_schema=None):
        body = dict(model=self.name, messages=messages, stream=False, think=False, keep_alive='2m',
                    options=dict(num_ctx=8192, num_predict=1800, temperature=0.2))
        if tools:
            body['tools'] = tools
        if format_schema is not None:
            body['format'] = format_schema
            body['options'].update(num_predict=192, temperature=0)
        try:
            async with httpx.AsyncClient(timeout=90, trust_env=False, transport=self.transport) as client:
                response = await client.post(self.url+'/api/chat', json=body)
                response.raise_for_status()
                message = response.json()['message']
            if not isinstance(message, dict) or message.get('role') != 'assistant':
                raise ValueError()
            # Reasoning is neither returned to the browser nor needed with think=False.
            return {key:value for key,value in message.items() if key in ('role','content','tool_calls')}
        except httpx.TimeoutException:
            raise AgentError('model_timeout', 'Локальная модель не успела ответить. Попробуйте более короткий запрос.', 504)
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            raise AgentError('model_unavailable', 'Локальная модель недоступна. Проверьте, что Ollama запущена и модель загружена.')

    async def select_facts(self, facts, question, limit):
        ids = [fact['id'] for fact in facts]
        schema = {
            'type': 'object', 'required': ['facts'], 'additionalProperties': False,
            'properties': {'facts': {'type': 'array', 'minItems': 1, 'maxItems': limit,
                                     'items': {'type': 'integer', 'enum': ids}}},
        }
        response = await self.reply([
            {'role': 'system', 'content': 'Выбери из списка подходящие факты для вопроса. Верни только JSON с их идентификаторами в массиве facts.'},
            {'role': 'user', 'content': json.dumps({'вопрос': question, 'факты': facts}, ensure_ascii=False)},
        ], [], format_schema=schema)
        try:
            chosen = json.loads(response['content'])['facts']
            if not isinstance(chosen, list) or not 1 <= len(chosen) <= limit:
                raise ValueError()
            if any(type(item) is not int or item not in ids for item in chosen):
                raise ValueError()
            return list(dict.fromkeys(chosen))
        except (ValueError, TypeError, KeyError):
            raise AgentError('invalid_model_evidence', 'Не удалось подобрать показатели для ответа. Уточните вопрос.', 502)
