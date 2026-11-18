import hmac
import json
import os
from app.analytics.contracts import AnalyticsError, Principal


def authenticate(header, config=None):
    configured = (config or {}).get('BALANCE_ANALYTICS_TOKENS') or os.environ.get('BALANCE_ANALYTICS_TOKENS', '')
    if not configured:
        raise AnalyticsError('auth_not_configured', 'Аналитический интерфейс не настроен: задайте BALANCE_ANALYTICS_TOKENS.', 503)
    try:
        registry = json.loads(configured) if isinstance(configured, str) else configured
        if not isinstance(registry, dict) or not registry:
            raise ValueError()
    except (ValueError, TypeError):
        raise AnalyticsError('auth_not_configured', 'Неверная конфигурация ключей аналитического интерфейса.', 503)
    scheme, _, token = (header or '').partition(' ')
    if scheme.lower() != 'bearer' or not token:
        raise AnalyticsError('unauthorized', 'Требуется Bearer-токен аналитического интерфейса.', 401)
    entry = next((entry for key, entry in registry.items() if hmac.compare_digest(key.encode(), token.encode())), None)
    if not isinstance(entry, dict):
        raise AnalyticsError('unauthorized', 'Недействительный токен.', 401)
    scopes = entry.get('scopes', [])
    if not isinstance(scopes, list) or any(not isinstance(scope, str) or not scope for scope in scopes):
        raise AnalyticsError('auth_not_configured', 'Права токена должны быть списком строк.', 503)
    if 'balance:read' not in scopes:
        raise AnalyticsError('insufficient_scope', 'Требуется право balance:read.', 403)
    for field in ('product_ids', 'basis_ids'):
        values = entry.get(field)
        if values is not None and (not isinstance(values, list) or any(type(value) is not int or value <= 0 for value in values)):
            raise AnalyticsError('auth_not_configured', 'Неверная конфигурация области доступа.', 503)
    if not isinstance(entry.get('subject'), str) or not entry['subject'].strip():
        raise AnalyticsError('auth_not_configured', 'Для ключа не указан субъект доступа.', 503)
    return Principal(entry['subject'], tuple(entry['product_ids']) if entry.get('product_ids') is not None else None,
                     tuple(entry['basis_ids']) if entry.get('basis_ids') is not None else None, tuple(scopes))
