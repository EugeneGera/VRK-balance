import json
import unittest
from unittest.mock import patch

import httpx
from fastmcp import Client
from mcp_server.server import Backend, create_server


class MCPToolsTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.requests = []

        def respond(request):
            self.requests.append(request)
            if request.url.params.get('products') == 'forbidden':
                return httpx.Response(403, json=dict(status='error', query_id='denied-query', error=dict(code='forbidden_filter', message='Denied')))
            return httpx.Response(200, json=dict(status='ok', metadata=dict(query_id='test-query', result_count=1,
                data_version=dict(snapshot_id='sha256:test')), data=dict(groups=[dict(unit=dict(id=2,name='тыс. т'), metrics=dict(allocated_volume=80))])))
        self.transport = httpx.MockTransport(respond)

    async def test_exactly_five_read_only_tools_are_discoverable(self):
        async with Client(create_server('http://balance.test', 'test-token', transport=self.transport)) as client:
            tools = await client.list_tools()
            self.assertEqual({tool.name for tool in tools}, {'get_data_catalog','get_filter_values','get_balance_summary','get_balance_details','compare_periods'})
            for tool in tools:
                self.assertTrue(tool.annotations.read_only_hint)
                self.assertFalse(tool.annotations.destructive_hint)
                self.assertIsNotNone(tool.input_schema)
                self.assertIsNotNone(tool.output_schema)

    async def test_structured_response_and_explicit_filters(self):
        async with Client(create_server('http://balance.test', 'test-token', transport=self.transport)) as client:
            result = await client.call_tool('get_balance_summary', dict(period=dict(year=2025, month_start=11), products=['АИ-92'], metrics=['allocated_volume']))
            self.assertEqual(result.structured_content['data']['groups'][0]['metrics']['allocated_volume'], 80)
        request = self.requests[0]
        self.assertEqual(request.url.params['products'], 'АИ-92')
        self.assertEqual(request.url.params['year'], '2025')
        self.assertEqual(request.headers['authorization'], 'Bearer test-token')
        self.assertEqual(request.method, 'GET')

    async def test_invalid_period_is_a_tool_error_without_backend_call(self):
        async with Client(create_server('http://balance.test', 'test-token', transport=self.transport)) as client:
            result = await client.call_tool('get_balance_summary', dict(period=dict(year=2025,month_start=12,month_end=1)), raise_on_error=False)
            self.assertTrue(result.is_error)
        self.assertEqual(self.requests, [])

    async def test_backend_error_remains_a_tool_error(self):
        async with Client(create_server('http://balance.test', 'test-token', transport=self.transport)) as client:
            result = await client.call_tool('get_balance_summary', dict(period=dict(year=2025,month_start=1), products=['forbidden']), raise_on_error=False)
            self.assertTrue(result.is_error)
            self.assertIn('forbidden_filter', str(result.content))
            self.assertIn('denied-query', str(result.content))

    async def test_http_never_falls_back_to_a_service_account_token(self):
        backend = Backend('http://balance.test', 'privileged-token', http_auth=True, transport=self.transport)
        with patch('mcp_server.server.get_access_token', return_value=None):
            with self.assertRaises(Exception) as context:
                await backend.call('get_data_catalog')
        self.assertIn('unauthorized', str(context.exception))
        self.assertEqual(self.requests, [])

    async def test_comparison_parameters_are_forwarded_without_mutations(self):
        async with Client(create_server('http://balance.test', 'test-token', transport=self.transport)) as client:
            await client.call_tool('compare_periods', dict(baseline=dict(year=2025,month_start=1),comparison=dict(year=2025,month_start=2)))
        self.assertEqual(self.requests[0].url.params['baseline_month_start'], '1')
        self.assertEqual(self.requests[0].url.params['comparison_month_start'], '2')


if __name__ == '__main__':
    unittest.main()
