"""Verify UI/API/MCP against the same fixed data; does not time human report creation."""
import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import sys
import time

import httpx
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

ROOT = Path(__file__).resolve().parents[1]
PATHS = dict(get_data_catalog='catalog', get_filter_values='filter-values', get_balance_summary='balance-summary',
             get_balance_details='balance-details', compare_periods='compare-periods')
TABLE_COLUMNS = dict(opening_stock=1,production_plan=2,available_resource=3,allocated_volume=4,domestic_volume=5,
                     exchange_volume=6,export_volume=15,own_needs_volume=19,unallocated_resource=21)


def query(arguments):
    values = {key: value for key, value in arguments.items() if key not in ('period','baseline','comparison')}
    values.update(arguments.get('period', {}))
    for prefix in ('baseline', 'comparison'):
        values.update({prefix+'_'+key: value for key, value in arguments.get(prefix, {}).items()})
    return {key: ','.join(value) if isinstance(value, list) else value for key, value in values.items()}


async def main(args):
    token = os.environ.get('BALANCE_ANALYTICS_TOKEN')
    if not token:
        raise SystemExit('Set BALANCE_ANALYTICS_TOKEN')
    fixtures = json.loads((ROOT/'experiments/control_cases.json').read_text())
    dump_sha256 = hashlib.sha256((ROOT/'BK.sql').read_bytes()).hexdigest()
    if dump_sha256 != fixtures['base_dump_sha256']:
        raise SystemExit('BK.sql differs from the fixed control dataset; restore it or review and update the controls.')
    target = args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, BALANCE_ANALYTICS_URL=args.base_url, BALANCE_ANALYTICS_TOKEN=token)
    transport = args.mcp_url if args.mcp_url else StdioTransport(sys.executable, ['-m','mcp_server.server'], env=env, cwd=str(ROOT))
    records = []
    async with Client(transport, auth=token if args.mcp_url else None) as mcp, httpx.AsyncClient(timeout=60, trust_env=False) as http:
        tools = await mcp.list_tools()
        assert {tool.name for tool in tools} == set(PATHS)
        for case in fixtures['cases']:
            started_at, clock = datetime.now(timezone.utc).isoformat(), time.monotonic()
            response = await http.get(args.base_url+'/analytics/'+PATHS[case['tool']], params=query(case['arguments']), headers={'Authorization':'Bearer '+token})
            api = response.json()
            result = await mcp.call_tool(case['tool'], case['arguments'], raise_on_error=False)
            if 'expected_error' in case:
                assert response.status_code == 400 and api['error']['code']==case['expected_error'], (case['id'],api)
                assert result.is_error,case['id']
                records.append(dict(case=case['id'],passed=True,status='expected_error',query_id=api['query_id']))
                continue
            assert response.status_code==200 and not result.is_error, (case['id'],api,result.content)
            payload = result.structured_content
            assert api['data']==payload['data'],case['id']
            assert api['metadata']['data_version']['snapshot_id']==payload['metadata']['data_version']['snapshot_id'],case['id']
            assert api['status']==case.get('expected_status','ok'),case['id']
            if 'expected' in case:
                actual=api['data']['groups'][0]['metrics']
                for metric,value in case['expected'].items():
                    assert actual[metric]==value,(case['id'],metric,actual[metric],value)
            if 'expected_unit_ids' in case:
                assert [group['unit']['id'] for group in api['data']['groups']]==case['expected_unit_ids']
            if 'expected_rows' in case:
                assert len(api['data']['rows'])==case['expected_rows']
            if 'expected_products' in case:
                assert len(api['data']['products'])==case['expected_products']
            if 'expected_change' in case:
                expected=case['expected_change'];actual=api['data']['groups'][0]['metrics'][expected['metric']]
                assert all(actual[key]==value for key,value in expected.items() if key!='metric'),case['id']
            if case.get('check_ui'):
                params=dict(case['arguments']['period'],category_product=case['arguments']['categories'][0],decimals=5,dash_zero=0)
                ui=await http.get(args.base_url+'/sankey/table',params=params)
                assert ui.status_code==200,(case['id'],ui.text)
                total=next(row for row in ui.json() if row[0]=='Итого')
                assert ui.headers['X-Data-Snapshot']==api['metadata']['data_version']['snapshot_id'],case['id']
                for metric,column in TABLE_COLUMNS.items():
                    value=api['data']['groups'][0]['metrics'][metric]
                    assert total[column] is None if value is None else abs(float(total[column])-value)<0.00001,(case['id'],metric,total[column],value)
            records.append(dict(case=case['id'],passed=True,started_at=started_at,finished_at=datetime.now(timezone.utc).isoformat(),
                api_query_id=api['metadata']['query_id'],mcp_query_id=payload['metadata']['query_id'],snapshot_id=api['metadata']['data_version']['snapshot_id'],
                request=case['arguments'],round_trip_ms=round((time.monotonic()-clock)*1000,3)))
    manifest=dict(passed=len(records),transport='http' if args.mcp_url else 'stdio',cases=records,
                  base_dump_sha256=dump_sha256,
                  runtime=dict(python=sys.version.split()[0], fastmcp=version('fastmcp'), httpx=version('httpx')),
                  edge_cases_sha256=hashlib.sha256((ROOT/'experiments/edge_cases.sql').read_bytes()).hexdigest())
    target.write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print(json.dumps(dict(passed=len(records),transport=manifest['transport'],output=str(target)),ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url',default=os.environ.get('BALANCE_ANALYTICS_URL','http://127.0.0.1:5001'))
    parser.add_argument('--mcp-url')
    parser.add_argument('--output',type=Path,default=ROOT/'experiments/results/controls.json')
    asyncio.run(main(parser.parse_args()))
