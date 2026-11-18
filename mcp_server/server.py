"""Run with python -m mcp_server.server --transport stdio|http."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import logging
import os
import time
from typing import Any
from urllib.parse import urlsplit
import uuid

import httpx
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.auth import AccessToken, TokenVerifier
from fastmcp.server.dependencies import get_access_token
from fastmcp.server.middleware import Middleware
from pydantic import BaseModel, ConfigDict, Field, model_validator

logger = logging.getLogger('balance.mcp.audit')
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False


class Period(BaseModel):
    """Inclusive month range within one year; omitted month_end means one month."""
    model_config = ConfigDict(extra='forbid')
    year: int = Field(ge=1, le=9999, strict=True)
    month_start: int = Field(ge=1, le=12, strict=True)
    month_end: int | None = Field(default=None, ge=1, le=12, strict=True)

    @model_validator(mode='after')
    def ordered(self):
        if self.month_end is not None and self.month_end < self.month_start:
            raise ValueError('month_end must be at least month_start')
        return self


class Backend:
    PATHS = dict(get_data_catalog='/catalog', get_filter_values='/filter-values',
                 get_balance_summary='/balance-summary', get_balance_details='/balance-details', compare_periods='/compare-periods')

    def __init__(self, base_url=None, token=None, http_auth=False, transport=None):
        self.base_url = (base_url or os.environ.get('BALANCE_ANALYTICS_URL', 'http://127.0.0.1:5001')).rstrip('/')
        parsed = urlsplit(self.base_url)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('BALANCE_ANALYTICS_URL must be an http(s) service URL without credentials, query or fragment')
        self.token = token or os.environ.get('BALANCE_ANALYTICS_TOKEN')
        self.http_auth, self.transport = http_auth, transport

    async def request(self, path, params, token):
        async with httpx.AsyncClient(timeout=30, follow_redirects=False, transport=self.transport, trust_env=False) as client:
            return await client.get(self.base_url+'/analytics'+path, params=params, headers={'Authorization':'Bearer '+token})

    async def call(self, tool, **params):
        access = get_access_token()
        token = access.token if access else None if self.http_auth else self.token
        if not token:
            raise ToolError(json.dumps(dict(code='unauthorized', message='Configure BALANCE_ANALYTICS_TOKEN for stdio or provide a Bearer token for HTTP.')))
        encoded = {key: ','.join(value) if isinstance(value, list) else value for key, value in params.items() if value is not None}
        try:
            response = await self.request(self.PATHS[tool], encoded, token)
            payload = response.json()
        except (httpx.HTTPError, ValueError):
            raise ToolError(json.dumps(dict(code='backend_unavailable', query_id=str(uuid.uuid4()), message='Balance analytics service is unavailable.')))
        if not isinstance(payload, dict):
            raise ToolError(json.dumps(dict(code='backend_error', query_id=str(uuid.uuid4()), message='Invalid analytics response.')))
        if response.status_code != 200 or payload.get('status') == 'error':
            # Only the API's deliberately public error fields are forwarded.
            error = payload.get('error', {}) if isinstance(payload, dict) else {}
            raise ToolError(json.dumps(dict(query_id=payload.get('query_id'), code=error.get('code', 'backend_error'),
                                           message=error.get('message', 'Analytics request failed.'), details=error.get('details', {})), ensure_ascii=False))
        return payload


class BalanceVerifier(TokenVerifier):
    def __init__(self, backend):
        super().__init__(required_scopes=['balance:read'])
        self.backend = backend

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            response = await self.backend.request('/access', {}, token)
            if response.status_code != 200:
                return None
            identity = response.json()['data']
            return AccessToken(token=token, client_id=identity['subject'], subject=identity['subject'], scopes=identity['scopes'],
                               claims={'iss': self.backend.base_url, 'sub': identity['subject']})
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            return None


class AuditMiddleware(Middleware):
    async def on_call_tool(self, context, call_next):
        query_id, started, clock = str(uuid.uuid4()), datetime.now(timezone.utc).isoformat(), time.monotonic()
        status, count = 'error', 0
        try:
            result = await call_next(context)
            status = 'ok'
            structured = getattr(result, 'structured_content', None) or getattr(result, 'structuredContent', None) or {}
            if isinstance(structured, dict):
                metadata = structured.get('metadata', {})
                query_id = metadata.get('query_id', query_id)
                count = metadata.get('result_count', 0)
                status = structured.get('status', status)
            return result
        except ToolError as error:
            try:
                details = json.loads(str(error))
                query_id = details.get('query_id') or query_id
            except (ValueError, TypeError, AttributeError):
                pass
            raise
        finally:
            arguments = {key: value for key, value in (context.message.arguments or {}).items()
                         if not any(word in key.lower() for word in ('token', 'secret', 'password', 'auth', 'key'))}
            logger.info(json.dumps(dict(query_id=query_id, tool=context.message.name,
                parameters=arguments, started_at=started,
                finished_at=datetime.now(timezone.utc).isoformat(), duration_ms=round((time.monotonic()-clock)*1000, 3),
                status=status, returned_records=count), ensure_ascii=False, sort_keys=True))


READ_ONLY = dict(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)


def create_server(base_url=None, token=None, http_auth=False, transport=None):
    backend = Backend(base_url, token, http_auth, transport)
    mcp = FastMCP('Production balance analytics', version='1.0.0',
        instructions='Read-only balance analysis. Discover metrics and units with get_data_catalog, then get_filter_values. '
                     'Always pass explicit periods. Keep unit groups separate. Preserve null as unknown; use backend differences and ratios. '
                     'Cite query_id, applied_filters and snapshot_id in reports. Do not treat errors as empty selections.',
        auth=BalanceVerifier(backend) if http_auth else None, middleware=[AuditMiddleware()], strict_input_validation=True)

    @mcp.tool(annotations=READ_ONLY)
    async def get_data_catalog() -> dict[str, Any]:
        """Describe available datasets, named metrics, formulas, units, supported filters, grouping and null/zero rules.

        Returns {status, metadata: {query_id, data_version}, data: {datasets, metrics, dimensions, period_rules, semantics}}.
        """
        return await backend.call('get_data_catalog')

    @mcp.tool(annotations=READ_ONLY)
    async def get_filter_values(period: Period | None = None, products: list[str] | None = None,
                                categories: list[str] | None = None, basises: list[str] | None = None) -> dict[str, Any]:
        """Discover permitted product/category/basis names and available periods, optionally narrowed by period and names.

        Returns numeric IDs, names, unit associations, available periods and a snapshot fingerprint. Only authorized entities are returned.
        """
        return await backend.call('get_filter_values', **(period.model_dump(exclude_none=True) if period else {}), products=products, categories=categories, basises=basises)

    @mcp.tool(annotations=READ_ONLY)
    async def get_balance_summary(period: Period, products: list[str] | None = None, categories: list[str] | None = None,
                                  basises: list[str] | None = None, metrics: list[str] | None = None, snapshot_id: str | None = None) -> dict[str, Any]:
        """Get supply, allocations, demand, remaining resource and backend-computed shares for an explicit period.

        Returns data.groups, one per unit, with numeric metrics, exact_metrics and null_reasons. Metadata contains the query ID,
        inclusive period, actually applied filters, source counts and snapshot_id. Optional snapshot_id rejects changed data with an error.
        """
        return await backend.call('get_balance_summary', **period.model_dump(exclude_none=True), products=products,
                                  categories=categories, basises=basises, metrics=metrics, snapshot_id=snapshot_id)

    @mcp.tool(annotations=READ_ONLY)
    async def get_balance_details(period: Period, group_by: list[str] = ['product', 'basis'], products: list[str] | None = None,
                                  categories: list[str] | None = None, basises: list[str] | None = None, metrics: list[str] | None = None,
                                  limit: int = 500, offset: int = 0, snapshot_id: str | None = None) -> dict[str, Any]:
        """Break down balance metrics by any unique combination of product, basis and month, keeping units separate.

        Returns data.rows with dimensions, unit, numeric metrics and exact_metrics. metadata.pagination reports total_count,
        limit, offset and has_more: request further pages rather than assuming the first page is complete. Limit: 1..10000.
        """
        return await backend.call('get_balance_details', **period.model_dump(exclude_none=True), group_by=group_by,
                                  products=products, categories=categories, basises=basises, metrics=metrics, limit=limit, offset=offset, snapshot_id=snapshot_id)

    @mcp.tool(annotations=READ_ONLY)
    async def compare_periods(baseline: Period, comparison: Period, products: list[str] | None = None,
                              categories: list[str] | None = None, basises: list[str] | None = None,
                              metrics: list[str] | None = None, snapshot_id: str | None = None) -> dict[str, Any]:
        """Compare two inclusive periods with identical filters using backend absolute changes and relative percentages.

        Returns groups per unit, with baseline/comparison values, absolute_change, percent_change and null_reason.
        Zero or missing baselines have null relative change. Percentage metrics use percentage points for absolute change.
        Both periods are read from one consistent database transaction; metadata identifies both source selections and the combined snapshot.
        """
        values = {prefix+key: value for prefix, period in [('baseline_', baseline), ('comparison_', comparison)] for key, value in period.model_dump(exclude_none=True).items()}
        return await backend.call('compare_periods', **values, products=products, categories=categories, basises=basises, metrics=metrics, snapshot_id=snapshot_id)

    return mcp


def main():
    parser = argparse.ArgumentParser(description='Read-only production balance MCP server')
    parser.add_argument('--transport', choices=['stdio', 'http'], default='stdio')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8001)
    args = parser.parse_args()
    if args.transport == 'stdio' and not os.environ.get('BALANCE_ANALYTICS_TOKEN'):
        parser.error('Set BALANCE_ANALYTICS_TOKEN for stdio. The token is checked by the Flask analytics API.')
    mcp = create_server(http_auth=args.transport == 'http')
    options = dict(host=args.host, port=args.port) if args.transport == 'http' else {}
    mcp.run(transport=args.transport, show_banner=False, **options)


if __name__ == '__main__':
    main()
