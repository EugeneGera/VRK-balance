import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.entities.models import Base, ProductCategoryDictModel, ProductDictModel, ProductionPlanModel, ShipmentsModel
from app.services.info_service import InfoService


class LatestPeriodTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.session.execute(ProductCategoryDictModel.__table__.insert(), [
            {'id': 101, 'name': 'Бензин АИ-92'},
            {'id': 104, 'name': 'ДТ'},
            {'id': 0, 'name': '0'},
        ])
        self.session.execute(ProductDictModel.__table__.insert(), [
            {'id': 1, 'name': 'Бензин АИ-92', 'tab_category_product_bk_ids': 101},
            {'id': 4, 'name': 'Топливо дизельное', 'tab_category_product_bk_ids': 104},
        ])
        self.service = InfoService(self.session)

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def add_data(self, year, month, category=101, product=1, **values):
        row = dict(id=str(self.session.query(ShipmentsModel).count() + 1),
                   year=year, month=month, tab_category_product_bk_ids=category,
                   tab_product_bk_ids=product, value=10)
        row.update(values)
        self.session.execute(ShipmentsModel.__table__.insert().values(**row))

    def test_empty_database(self):
        self.assertIsNone(self.service.get_latest_period())

    def test_latest_year_and_month_are_one_period(self):
        self.add_data(2024, 12)
        self.add_data(2025, 2)
        self.add_data(2025, 1)
        self.assertEqual(self.service.get_latest_period(), {
            'year': 2025, 'month_start': 2, 'category_product': 'Бензин АИ-92',
        })

    def test_future_empty_rows_and_invalid_months_are_ignored(self):
        self.add_data(2025, 12)
        self.add_data(2026, 1, value=0)
        self.add_data(2027, 13)
        self.add_data(2027, 0)
        self.assertEqual(self.service.get_latest_period()['year'], 2025)

    def test_resource_without_applications_is_available(self):
        self.add_data(2025, 11)
        self.add_data(2025, 12, value=0, all_resourse=30)
        self.assertEqual(self.service.get_latest_period()['month_start'], 12)

    def test_future_production_plan_does_not_change_dashboard_period(self):
        self.add_data(2025, 12)
        self.session.execute(ProductionPlanModel.__table__.insert().values(
            id=1, year=2026, month=12, plan=100, tab_product_bk_ids=1,
        ))
        self.assertEqual(self.service.get_latest_period()['year'], 2025)

    def test_category_is_available_in_the_latest_period(self):
        self.add_data(2025, 11)
        self.add_data(2025, 12, category=104, product=4)
        self.assertEqual(self.service.get_latest_period()['category_product'], 'ДТ')

    def test_unknown_products_and_placeholder_categories_are_ignored(self):
        self.add_data(2025, 12)
        self.add_data(2026, 1, category=0)
        self.add_data(2026, 2, product=999)
        self.assertEqual(self.service.get_latest_period()['year'], 2025)


if __name__ == '__main__':
    unittest.main()
