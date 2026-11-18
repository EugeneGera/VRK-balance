import argparse
import asyncio
from datetime import datetime, timezone
import json
import logging
import time
import uuid

from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn

from agent_server.contracts import AgentError,ChatRequest
from agent_server.engine import Analyst

logger=logging.getLogger('balance.agent.audit')
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)
logger.propagate=False


def create_app(analyst=None):
    analyst=analyst or Analyst()

    async def handle(request:Request):
        request_id,started,clock=str(uuid.uuid4()),datetime.now(timezone.utc).isoformat(),time.monotonic()
        status,action,count='error',request.url.path,0
        report_id, error_code, outcome = None, None, 'error'
        audit = {}
        try:
            scheme,_,token=request.headers.get('authorization','').partition(' ')
            if scheme.lower()!='bearer' or not token:
                raise AgentError('unauthorized','Требуется ключ доступа к аналитике.',401)
            if request.url.path=='/status':
                # Validate the caller through the same MCP connection; never use
                # a privileged token as fallback inside this process.
                async with analyst.client_factory(token) as client:
                    await analyst.call(client,'get_data_catalog',{},[])
                data=await analyst.model.status()
                data['profile'] = 'experiment' if analyst.experiment_digest else 'local'
            elif request.url.path=='/filter-values':
                data=await analyst.filters(token)
            else:
                raw=bytearray()
                async for chunk in request.stream():
                    if len(raw)+len(chunk)>100000:
                        raise AgentError('request_too_large','Слишком длинный диалог.',413)
                    raw.extend(chunk)
                body=ChatRequest.model_validate_json(raw)
                action=body.action
                data=await asyncio.wait_for(analyst.run(body,token,audit),timeout=240)
                count=len(data['tables'])
                outcome = data['kind']
                report_id = data['id'] if outcome == 'report' else None
            status='ok'
            if request.url.path != '/chat':
                outcome = 'metadata'
            return JSONResponse(dict(status='ok',request_id=request_id,data=data))
        except ValidationError:
            error_code='invalid_request'
            return JSONResponse(dict(status='error',request_id=request_id,error=dict(code='invalid_request',message='Проверьте период, фильтры и длину сообщения.')),status_code=400)
        except AgentError as error:
            error_code=error.code
            return JSONResponse(dict(status='error',request_id=request_id,error=dict(code=error.code,message=error.message,query_id=error.query_id)),status_code=error.status)
        except asyncio.TimeoutError:
            error_code='analysis_timeout'
            return JSONResponse(dict(status='error',request_id=request_id,error=dict(code='analysis_timeout',message='Анализ занял слишком много времени. Уточните запрос.')),status_code=504)
        except Exception:
            error_code='agent_unavailable'
            return JSONResponse(dict(status='error',request_id=request_id,error=dict(code='agent_unavailable',message='Не удалось связаться с сервисом аналитики.')),status_code=503)
        finally:
            logger.info(json.dumps(dict(request_id=request_id,action=action,started_at=started,
                finished_at=datetime.now(timezone.utc).isoformat(),duration_ms=round((time.monotonic()-clock)*1000,3),
                status=status,outcome=outcome,error_code=error_code,returned_tables=count,report_id=report_id,
                clarification_count=int(outcome == 'clarification'),**audit),ensure_ascii=False))

    return Starlette(routes=[Route('/status',handle),Route('/filter-values',handle),Route('/chat',handle,methods=['POST'])])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--host',default='127.0.0.1')
    parser.add_argument('--port',type=int,default=8002)
    args=parser.parse_args()
    uvicorn.run(create_app(),host=args.host,port=args.port,log_level='warning')


if __name__=='__main__':
    main()
