"""Browser gateway; credentials stay on the server, calculations stay in MCP."""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler

from flask import Blueprint, current_app, jsonify, request
from app.analytics.access import authenticate
from app.analytics.contracts import AnalyticsError

assistant_blueprint=Blueprint('assistant',__name__,url_prefix='/assistant')


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def caller_token():
    header=request.headers.get('Authorization')
    if not header:
        token=current_app.config.get('BALANCE_ASSISTANT_TOKEN') or os.environ.get('BALANCE_ASSISTANT_TOKEN')
        if not token:
            raise AnalyticsError('assistant_not_configured','Помощник ещё не настроен. Создайте конфигурацию аналитики и запустите сервис агента.',503)
        header='Bearer '+token
    authenticate(header,current_app.config)
    return header.partition(' ')[2]


def forward(path,method='GET'):
    try:
        token=caller_token()
        if request.args:
            raise AnalyticsError('unsupported_parameter','Параметры передаются в теле запроса, не в URL.')
        body=request.stream.read(100001) if method=='POST' else None
        if body is not None and len(body)>100000:
            raise AnalyticsError('request_too_large','Слишком длинный диалог.',413)
        url=(current_app.config.get('BALANCE_AGENT_URL') or os.environ.get('BALANCE_AGENT_URL','http://127.0.0.1:8002')).rstrip('/')
        parsed=urlsplit(url)
        if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise AnalyticsError('assistant_not_configured','Неверный адрес сервиса аналитики.',503)
        upstream=Request(url+path,data=body,method=method,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
        opener=build_opener(ProxyHandler({}),NoRedirect())
        try:
            response=opener.open(upstream,timeout=250)
        except HTTPError as error:
            response=error
        with response:
            raw=response.read(2000001)
            if len(raw)>2000000:
                raise ValueError('oversized response')
            payload=json.loads(raw)
            if not isinstance(payload,dict) or payload.get('status') not in ('ok','error'):
                raise ValueError('invalid response')
            return jsonify(payload),response.code
    except AnalyticsError as error:
        return jsonify(status='error',error=dict(code=error.code,message=error.message)),error.status
    except (URLError,OSError,ValueError,TypeError):
        return jsonify(status='error',error=dict(code='agent_unavailable',message='Сервис аналитики недоступен. Проверьте его запуск.')),503


@assistant_blueprint.get('/status')
def status():
    return forward('/status')


@assistant_blueprint.get('/filter-values')
def filters():
    return forward('/filter-values')


@assistant_blueprint.post('/chat')
def chat():
    return forward('/chat','POST')
