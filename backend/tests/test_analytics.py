import json
import unittest
from decimal import Decimal
from unittest.mock import patch

from flask import Flask
from flask_restx import Api
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from app.analytics.api import blueprint
from app.analytics.balance import BalanceData, compare_data
from app.analytics.contracts import AnalyticsError, QuerySpec, nullable_sum
from app.analytics.legacy import BalancePresentation
from app.analytics import transport
from app.apis.ns_sankey import ns_sankey
from app.apis.utils import get_months
from app.entities.models import (Base, ProductDictModel as Product, ProductCategoryDictModel as Category,
    UnitDictModel as Unit, ShippingBasisDictModel as Basis, ProductionPlanModel as Plan,
    AllResourceModel as Resource, ShipmentsModel as Shipment, TransDirDictModel as Direction, DealCategoryDictModel as Deal)
from app.services.shipments_service import ShipmentsService
from app.services.info_service import InfoService


class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.session.execute(Unit.__table__.insert(), [dict(id=2, name='тыс. т'), dict(id=3, name='тыс. м3')])
        self.session.execute(Category.__table__.insert(), [dict(id=101, name='Бензин'), dict(id=118, name='Гелий')])
        self.session.execute(Product.__table__.insert(), [dict(id=1, name='АИ-92', tab_category_product_bk_ids=101, tab_ei_bk_ids=2),
            dict(id=2, name='АИ-95', tab_category_product_bk_ids=101, tab_ei_bk_ids=2),
            dict(id=24, name='Гелий', tab_category_product_bk_ids=118, tab_ei_bk_ids=3)])
        self.session.execute(Basis.__table__.insert(), [dict(id=1, name='Север'), dict(id=2, name='Юг')])
        self.session.execute(Direction.__table__.insert(), [dict(id=1, name='нужды ДО'), dict(id=2, name='внутренний рынок'), dict(id=3, name='экспорт')])
        self.session.execute(Deal.__table__.insert(), [dict(id=i, name='Категория '+str(i), tab_type_sd_bk_ids=1, tab_kanal_sb_bk_ids=1) for i in range(1, 10)])
        self.session.commit()
        self.app = Flask(__name__)
        self.app.config.update(TESTING=True, SECRET_KEY='test', BALANCE_ANALYTICS_TOKENS=json.dumps({
            'test-reader': dict(subject='reader', scopes=['balance:read']),
            'test-limited': dict(subject='limited', scopes=['balance:read'], product_ids=[1], basis_ids=[1]),
            'test-no-scope': dict(subject='other', scopes=[]),
        }))
        self.app.register_blueprint(blueprint)
        Api(self.app).add_namespace(ns_sankey, path='/sankey')
        self.client = self.app.test_client()
        self.db_patch = patch.object(transport, 'set_db_connection', lambda: self.session)
        self.db_patch.start()
        self.serial = 0

    def tearDown(self):
        self.db_patch.stop()
        self.session.close()
        self.engine.dispose()

    def add_point(self, month=1, product=1, basis=1, year=2025, plan=100, opening=10, resource=100,
                  requested=95, accepted=80, unit=None, deal=3, direction=2):
        self.serial += 1
        unit = unit or (3 if product == 24 else 2)
        common = dict(year=year, month=month, tab_product_bk_ids=product, tab_bazis_bk_ids=basis)
        self.session.execute(Plan.__table__.insert().values(**common, id=self.serial, tab_ei_bk_ids=unit,
            tab_sobstv_bk_ids=1, plan=plan, ost=opening, min_ost=0, max_otgr=0))
        self.session.execute(Resource.__table__.insert().values(**common, plan=plan, ost=opening, summ_res=resource,
            ogr=None if plan is None or opening is None or resource is None else plan+opening-resource))
        self.session.execute(Shipment.__table__.insert().values(**common, id='row-'+str(self.serial),
            tab_owner_bk_ids=1, tab_sobstv_bk_ids=1, tab_ei_bk_ids=unit, id_zayav_real=self.serial,
            tab_napr_real_bk_ids=direction, tab_category_sd_bk_ids=deal, value=requested, accept_zayav=accepted, cost=123.45))
        self.session.commit()

    def get(self, endpoint='balance-summary', token='test-reader', **params):
        if endpoint in ('balance-summary', 'balance-details'):
            params = dict(year=2025, month_start=1, **params)
        headers = {'Authorization': 'Bearer '+token} if token else {}
        return self.client.get('/analytics/'+endpoint, query_string=params, headers=headers)

    def test_no_session_required_and_same_category_products_do_not_stick(self):
        service = ShipmentsService(self.session)
        service.update_product_filter(2025, [1], None, ['АИ-92'], ['Бензин'])
        self.assertEqual(service.product_names, ['АИ-92'])
        service.update_product_filter(2025, [1], None, ['АИ-95'], ['Бензин'])
        self.assertEqual(service.product_names, ['АИ-95'])
        self.assertEqual(len(InfoService(self.session).get_products_names_filtered()['products']), 3)

    def test_numbers_and_zero_missing_are_distinct(self):
        self.add_point(plan=None, opening=0, resource=0, requested=0, accepted=0)
        response = self.get()
        self.assertEqual(response.status_code, 200)
        metrics = response.json['data']['groups'][0]['metrics']
        self.assertIsNone(metrics['production_plan'])
        self.assertEqual(metrics['available_resource'], 0)
        self.assertEqual(metrics['allocated_volume'], 0)
        self.assertIsNone(metrics['utilization_percent'])
        self.assertEqual(response.json['data']['groups'][0]['null_reasons']['utilization_percent'], 'zero_denominator')

    def test_same_owner_multiple_products_are_summed_once_each(self):
        self.add_point(product=1, resource=100)
        self.add_point(product=2, resource=200, plan=200, accepted=150, requested=160)
        metrics = self.get().json['data']['groups'][0]['metrics']
        self.assertEqual(metrics['available_resource'], 300)
        self.assertEqual(metrics['allocated_volume'], 230)
        self.assertEqual(metrics['unallocated_resource'], 70)

    def test_incompatible_units_are_separate(self):
        self.add_point(product=1)
        self.add_point(product=24, resource=50, accepted=40, requested=45)
        groups = self.get().json['data']['groups']
        self.assertEqual([row['unit']['id'] for row in groups], [2, 3])
        self.assertEqual([row['metrics']['allocated_volume'] for row in groups], [80, 40])
        response = self.client.get('/sankey/table', query_string=dict(year=2025, month_start=1))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error']['code'], 'incompatible_units')

    def test_missing_value_is_not_silently_dropped(self):
        self.add_point(product=1, accepted=None)
        self.add_point(product=2)
        self.assertIsNone(self.get().json['data']['groups'][0]['metrics']['allocated_volume'])

    def test_full_year_is_not_truncated_to_three_months(self):
        for month in range(1, 13):
            self.add_point(month=month)
        response = self.get(month_end=12)
        self.assertEqual(response.json['data']['groups'][0]['metrics']['production_plan'], 1200)
        self.assertEqual(response.json['metadata']['period']['month_end'], 12)
        self.assertEqual(len(get_months(dict(year=2025, month_start=1, month_end=12), limit=3)), 12)

    def test_invalid_periods_and_unknown_parameters(self):
        for query in [dict(year=2025, month_start=0), dict(year=2025, month_start=13),
                      dict(year=2025, month_start=4, month_end=2), dict(year=2025, month_start=1, year_end=2026),
                      dict(month_start=1), dict(year=2025, month_start=1, products='Неверный продукт')]:
            response = self.client.get('/analytics/balance-summary', query_string=query, headers={'Authorization':'Bearer test-reader'})
            self.assertEqual(response.status_code, 400, query)
            self.assertEqual(response.json['status'], 'error')
            self.assertIn('query_id', response.json)

    def test_authentication_and_permissions(self):
        self.add_point(product=1)
        self.add_point(product=2, basis=2, year=2026)
        self.assertEqual(self.get(token=None).status_code, 401)
        self.assertEqual(self.get(token='invalid').status_code, 401)
        self.assertEqual(self.get(token='test-no-scope').status_code, 403)
        self.assertEqual(self.get(token='test-limited', products='АИ-95').status_code, 403)
        self.assertEqual(self.get(token='test-limited', basises='Юг').status_code, 403)
        allowed = self.get(token='test-limited')
        self.assertEqual(allowed.status_code, 200)
        values = self.get('filter-values', token='test-limited').json['data']
        self.assertEqual([p['id'] for p in values['products']], [1])
        self.assertEqual(values['periods'], [dict(year=2025, month=1)])

    def test_mutating_endpoints_are_not_exposed(self):
        response = self.client.put('/analytics/balance-summary', json={}, headers={'Authorization':'Bearer test-reader'})
        self.assertEqual(response.status_code, 405)

    def test_snapshot_is_stable_but_request_id_is_unique(self):
        self.add_point()
        a, b = self.get().json, self.get().json
        self.assertNotEqual(a['metadata']['query_id'], b['metadata']['query_id'])
        self.assertEqual(a['metadata']['data_version']['snapshot_id'], b['metadata']['data_version']['snapshot_id'])
        self.session.execute(Resource.__table__.update().values(summ_res=101))
        self.session.commit()
        changed = self.get(snapshot_id=a['metadata']['data_version']['snapshot_id'])
        self.assertEqual(changed.status_code, 409)

    def test_empty_and_database_error_are_distinct(self):
        empty = self.get()
        self.assertEqual(empty.status_code, 200)
        self.assertEqual(empty.json['status'], 'empty')
        with patch.object(transport, 'set_db_connection', side_effect=OperationalError('test', {}, Exception('offline'))):
            unavailable = self.get()
        self.assertEqual(unavailable.status_code, 503)
        self.assertEqual(unavailable.json['error']['code'], 'database_unavailable')

    def test_catalog_does_not_require_database_connection(self):
        with patch.object(transport, 'set_db_connection', side_effect=AssertionError('database should not be accessed')):
            response = self.get('catalog')
        self.assertEqual(response.status_code, 200)
        self.assertIn('available_resource', response.json['data']['metrics'])

    def test_calculation_error_is_not_an_empty_selection(self):
        self.add_point(accepted=-5)
        response = self.get()
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json['error']['code'], 'invalid_allocation')

    def test_duplicate_actual_application_is_rejected(self):
        self.add_point(product=1)
        self.add_point(product=2)
        self.session.execute(Shipment.__table__.update().values(id_zayav_real=1))
        self.session.commit()
        response = self.get()
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json['error']['code'], 'duplicate_application')

    def test_technical_placeholder_does_not_count_as_an_application(self):
        self.add_point(accepted=0, requested=0)
        self.session.execute(Shipment.__table__.update().values(id_zayav_real=None, value=None, accept_zayav=None))
        self.session.commit()
        metrics = self.get().json['data']['groups'][0]['metrics']
        self.assertEqual(metrics['application_count'], 0)
        self.assertEqual(metrics['allocated_volume'], 0)

    def test_precision_and_ui_match_the_analytical_api(self):
        self.assertEqual(nullable_sum([Decimal('.1'), Decimal('.2')]), Decimal('.3'))
        self.add_point(accepted=12.34567, requested=20)
        raw = self.get().json['data']['groups'][0]['metrics']
        self.assertEqual(raw['allocated_volume'], 12.34567)
        table = self.client.get('/sankey/table', query_string=dict(year=2025, month_start=1, category_product='Бензин', decimals=5, dash_zero=0))
        self.assertEqual(table.status_code, 200)
        total = next(row for row in table.json if row[0] == 'Итого')
        self.assertAlmostEqual(float(total[4]), raw['allocated_volume'], places=5)
        waterfall = self.client.get('/sankey/waterfall', query_string=dict(year=2025, month_start=1, category_product='Бензин'))
        total_chart = next(row['data'] for row in waterfall.json['data']['data'] if row['name']=='Total')
        self.assertEqual(total_chart['available_resource']['available'], raw['available_resource'])
        self.assertIn('X-Data-Snapshot', table.headers)

    def test_period_comparison_handles_zero_and_missing_baselines(self):
        self.add_point(month=1, resource=0, accepted=0, requested=0, plan=0, opening=0)
        self.add_point(month=2)
        args = dict(baseline_year=2025, baseline_month_start=1, comparison_year=2025, comparison_month_start=2, metrics='allocated_volume')
        response = self.get('compare-periods', **args)
        self.assertEqual(response.status_code, 200)
        metric = response.json['data']['groups'][0]['metrics']['allocated_volume']
        self.assertEqual(metric['absolute_change'], 80)
        self.assertIsNone(metric['percent_change'])
        self.assertEqual(metric['null_reason'], 'zero_baseline')

    def test_detail_pagination_is_explicit(self):
        self.add_point(product=1)
        self.add_point(product=2)
        response = self.get('balance-details', group_by='product', limit=1)
        self.assertEqual(len(response.json['data']['rows']), 1)
        self.assertEqual(response.json['metadata']['pagination'], dict(total_count=2, limit=1, offset=0, has_more=True))
        self.assertEqual(self.get('balance-details', group_by='invalid').status_code, 400)

    def test_queries_do_not_set_browser_filters_and_are_audited(self):
        self.add_point(product=1)
        self.add_point(product=2)
        with self.assertLogs(transport.audit, level='INFO') as records:
            first = self.get(products='АИ-92')
            second = self.get(products='АИ-95')
        self.assertEqual(first.json['metadata']['applied_filters']['products'][0]['name'], 'АИ-92')
        self.assertEqual(second.json['metadata']['applied_filters']['products'][0]['name'], 'АИ-95')
        self.assertNotIn('Set-Cookie', first.headers)
        self.assertNotIn('test-reader', '\n'.join(records.output))
        event = json.loads(records.output[0].split(':', 2)[2])
        self.assertEqual(event['operation'], 'get_balance_summary')
        self.assertIn('duration_ms', event)
        self.assertEqual(event['returned_records'], 1)


if __name__ == '__main__':
    unittest.main()
