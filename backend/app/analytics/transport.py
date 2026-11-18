from datetime import datetime, timezone
from functools import wraps
import json
import logging
import time
import uuid

from flask import current_app, jsonify, request
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from app.analytics.access import authenticate
from app.analytics.contracts import AnalyticsError, json_numbers
from app.entities.db_connection import set_db_connection

audit = logging.getLogger('balance.analytics.audit')
if not audit.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    audit.addHandler(handler)
audit.setLevel(logging.INFO)
audit.propagate = False


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def read_endpoint(operation, protected=True, database=True):
    def decorate(handler):
        @wraps(handler)
        def execute(*args, **kwargs):
            query_id, started_at, clock = str(uuid.uuid4()), utcnow(), time.monotonic()
            session, principal, metadata, count, status, error_code = None, None, {}, 0, 'error', None
            try:
                principal = authenticate(request.headers.get('Authorization'), current_app.config) if protected else None
                if database:
                    session = set_db_connection()
                    if session.get_bind().dialect.name == 'postgresql':
                        session.connection(execution_options={'isolation_level': 'REPEATABLE READ'})
                        session.execute(text('SET TRANSACTION READ ONLY'))
                data, metadata, count, empty = handler(*args, session=session, principal=principal, **kwargs)
                status = 'empty' if empty else 'ok'
                metadata = dict(metadata, query_id=query_id, actor=principal.subject if principal else 'browser',
                                started_at=started_at, finished_at=utcnow(), result_count=count)
                body = dict(status=status, metadata=metadata, data=json_numbers(data)) if protected else json_numbers(data)
                response = jsonify(body)
                response.headers['X-Query-ID'] = query_id
                if metadata.get('data_version', {}).get('snapshot_id'):
                    response.headers['X-Data-Snapshot'] = metadata['data_version']['snapshot_id']
                return response
            except AnalyticsError as error:
                status = 'error'
                error_code = error.code
                response = jsonify(status='error', query_id=query_id, error=dict(code=error.code, message=error.message, details=error.details))
                response.status_code = error.status
                if error.status == 401:
                    response.headers['WWW-Authenticate'] = 'Bearer realm="balance-analytics"'
                return response
            except OperationalError:
                status = 'error'
                error_code = 'database_unavailable'
                return jsonify(status='error', query_id=query_id, error=dict(code=error_code, message='База данных недоступна.')), 503
            except SQLAlchemyError:
                status = 'error'
                error_code = 'calculation_error'
                return jsonify(status='error', query_id=query_id, error=dict(code=error_code, message='Не удалось выполнить запрос данных.')), 500
            except Exception:
                status = 'error'
                error_code = 'internal_error'
                return jsonify(status='error', query_id=query_id, error=dict(code=error_code, message='Внутренняя ошибка обработки запроса.')), 500
            finally:
                if session is not None:
                    try:
                        session.rollback()
                        session.close()
                    except SQLAlchemyError:
                        pass
                event = dict(query_id=query_id, operation=operation, subject=principal.subject if principal else 'browser' if not protected else None,
                             parameters={key: request.args.getlist(key) for key in request.args if not any(word in key.lower() for word in ('token', 'secret', 'password', 'auth', 'key'))}, started_at=started_at,
                             finished_at=utcnow(), duration_ms=round((time.monotonic() - clock) * 1000, 3),
                             status=status, error_code=error_code, returned_records=count,
                             snapshot_id=metadata.get('data_version', {}).get('snapshot_id'))
                audit.info(json.dumps(event, ensure_ascii=False, sort_keys=True))
        return execute
    return decorate
