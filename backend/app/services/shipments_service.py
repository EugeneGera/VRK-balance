from typing import List, Optional, Union
from sqlalchemy.orm import scoped_session

from app.entities.schemas import products_list_schema, basises_list_schema, category_products_list_schema
from app.repositories.dict_repositories import ProductDictRepository, ShippingBasisDictRepository, ProductCategoryDictRepository
from app.repositories.shipments_repository import ShipmentsRepository
from app.utils import round_to_significant, safe_none_sum, zero_to_none
from app.services.filter_service import product_filters
from app.analytics.legacy import BalancePresentation
from app.analytics.contracts import AnalyticsError


class ShipmentsService:
    def __init__(self, session: scoped_session):
        self.session = session
        self.product_dict_repository = ProductDictRepository(session)
        self.category_product_dict_repository = ProductCategoryDictRepository(session)
        self.basises_dict_repository = ShippingBasisDictRepository(session)
        self.shipments_repository = ShipmentsRepository(session)
        self.product_ids: Optional[Union[List[int], int]] = None
        self.product_names: Optional[Union[List[str], str]] = None
        self.unit_names: Optional[Union[List[str], str]] = None



    def _balance_view(self, year, months, basises, products, categories):
        if not months or sorted(set(months)) != list(range(min(months), max(months) + 1)):
            raise AnalyticsError('invalid_period', 'Период должен быть непустым непрерывным диапазоном месяцев.')
        return BalancePresentation(self.session, dict(year=year, month_start=min(months), month_end=max(months),
                                  basises=basises, product=products, category_product=categories))

    def update_product_filter(self, year: int, months: List[int], basis_names: List[str],
                              product_names: Optional[Union[List[str], str]] = None,
                              category_names: Optional[Union[List[str], str]] = None):
        updated_filters = product_filters(session=self.session,
                                                                     year=year, months=months,
                                                                     basis_names=basis_names,
                                                                     product_names=product_names,
                                                                     category_names=category_names)
        self.product_ids = updated_filters.get('product_ids', None)
        self.product_names = updated_filters.get('product_names', None)
        self.unit_names = updated_filters.get('unit_names', None)
        self.category_names = updated_filters.get('category_names', None)
        

    
    def get_shipped_unit_names(self, year, months, products=None, category_product=None, basises=None):
        return self._balance_view(year, months, basises, products, category_product).unit

    def get_products_names(self):
        names_list = self.product_dict_repository.get_names()
        return products_list_schema.dump({'products': names_list})

    def get_category_product_names(self):
        names_list = self.category_product_dict_repository.get_names()
        return category_products_list_schema.dump({'category_product': names_list})

    def get_shipped_products_names(self, year: int, months: List[int], basises: Optional[List[str]] = None):
        rows = self.shipments_repository.get_shipped_products_names(
            year=year, months=months, basis_names=basises)
        names_list = [row[0] for row in rows]
        return names_list

    def get_basises_names(self):
        names_list = self.basises_dict_repository.get_names()
        return basises_list_schema.dump({'shipping_basises': names_list})

    # def _add_unallocated_flow(self, basis: str, volume: float, sankey_flows: List, kind: str):
    #     if basis is None:
    #         return

    #     flow_data = {
    #         'source': basis,
    #         'target': 'нераспределённый ресурс',
    #         'target_kind': None,
    #         'kind': kind,
    #         'value': None if volume is None else max(volume, 0)
    #     }
    #     sankey_flows.append(SankeySingularFlowSchema().load(flow_data))

    def get_sankey_data(self, year, months, basises=None, products=None, category_product=None, grouping_base=None):
        view = self._balance_view(year, months, basises, products, category_product)
        view.args['grouping_mode'] = grouping_base or 'factories'
        return view.graph()[0]
            
    def get_stock_details(self, year, months, basises=None, products=None, category_product=None):
        return self._balance_view(year, months, basises, products, category_product).stock()[0]




    def get_factory_details(self, 
                            year: int,
                            months: List[int],
                            basises: Optional[List[str]] = None,
                            products: Optional[Union[List[str], str]] = None,
                            category_product: Optional[Union[List[str], str]] = None):

        self.update_product_filter(product_names=products,
                                   year=year,
                                   months=months,
                                   basis_names=basises,
                                   category_names=category_product)


        total_left = 0
        total_plan = 0
        total_all_resource = 0
        total_applications = 0
        total_delta = None
        total_restrictions = None
        total_percent = 0
        factory_leftovers_rows = self.shipments_repository.get_factory_leftovers(year=year,
                                                                                 months=months,
                                                                                 basis_names=basises,
                                                                                 product_names=self.product_names,
                                                                                 category_names=self.category_names)
        
        factory_leftover_data_left = []
        factory_leftover_data_right = []

        for row in factory_leftovers_rows:
            if not any([row.left, row.plan, row.all_resource, row.restrictions, row.applications, row.delta]):
                continue
            total_left += 0 if row.left is None else row.left
            total_plan += 0 if row.plan is None else row.plan
            total_delta = safe_none_sum(total_delta, None if row.applications is None else row.delta)
            total_applications = safe_none_sum(row.applications, total_applications)
            total_restrictions = safe_none_sum(row.restrictions, total_restrictions)
            total_all_resource += 0 if row.all_resource is None else row.all_resource
            total_percent = None if (total_all_resource) == 0 else float(total_applications) / float(total_all_resource)*100

            data = {
                'factory_name': row.factory_name,
                'leftovers': [
                    {
                        'type': 'Остатки',
                        'category': 'план',
                        'value': zero_to_none(row.left)
                    },
                    {
                        'type': 'План производства',
                        'category': 'план',
                        'value': zero_to_none(row.plan),
                    },
                    {
                        'type': 'Ресурс к распределению',
                        'category': 'ресурс',
                        'value': zero_to_none(row.all_resource),
                    },
                    {
                        'type': 'Ограничения',
                        'category': 'ресурс',
                        'value': zero_to_none(row.restrictions),
                    },
                    {
                        'type': 'Заявки',
                        'category': 'заявки',
                        'value': zero_to_none(row.applications),
                    },
                    {
                        'type': 'Дельта',
                        'category': 'заявки',
                        'value': None if row.applications is None else zero_to_none(row.delta)
                    }
                ]
            }
            # print(row.applications, type(row.applications), zero_to_none(row.applications))
            if row.plan is None or row.plan == 0:
                factory_leftover_data_left.append(data)
            else:
                factory_leftover_data_right.append(data)
        
        return {
            'pie_left_plan_data': [
                {
                    'type': 'Остатки',
                    'value': total_left        
                },
                {
                    'type': 'План производства',
                    'value': total_plan,
                    'delta': total_delta
                }
            ],
            'total_percent': {'value': total_percent},
            'pie_resource_restriction': [
                {
                    'type': 'Ресурс к распределению',
                    'value': total_all_resource
                },
                {
                    'type': 'Ограничения',
                    'value': total_restrictions
                }
            ],
            'pie_progress_application': {
                'type': 'Заявки',
                'percent': None if (total_left + total_plan) == 0 else float(total_applications) / float(total_left + total_plan),
                'value': total_applications,
            },
            'pie_progress_delta': {
                'type': 'Дельта',
                'percent': None if (total_all_resource - total_applications) == 0 else abs(float(total_all_resource) / float(
                    total_all_resource - total_applications)),
                'value': total_delta,
            },
            'factory_leftover_data': factory_leftover_data_left + factory_leftover_data_right,
            'unit' : self.unit_names
        }

        # print(rows_dict[key])


    def get_table(self, year, months, basises=None, products=None, category_product=None):
        return self._balance_view(year, months, basises, products, category_product).table(formatted=False)[0]

    def get_factory_income(self,
                           year: int,
                           months: List[int],
                           basises: Optional[List[str]] = None,
                           products: Optional[Union[List[str], str]] = None,
                           category_product: Optional[Union[List[str], str]] = None):
        self.update_product_filter(product_names=products,
                                   year=year,
                                   months=months,
                                   basis_names=basises,
                                   category_names=category_product)
        table_data_rows = self.shipments_repository.get_factory_income(year=year,
                                                                       months=months,
                                                                       basis_names=basises,
                                                                       product_names=self.product_names,
                                                                       category_names=self.category_names,)
        
        # Создаем структуру для заводов
        factories = {}

        # Обрабатываем каждую строку данных
        for row in table_data_rows:
            factory_name = row.shipping_basis
            trans_dir = row.trans_dir
            unit = row.unit
            
            # Приводим названия типов к нужному формату
            if trans_dir == "внутренний рынок":
                type_name = "Вн. рынок"
            elif trans_dir == "экспорт":
                type_name = "Экспорт"
            else:
                type_name = trans_dir             
           
            if (( row.total_cost is not None and row.total_cost != 0 ) or 
                ( row.cost is not None and row.cost != 0 ) or 
                ( row.total_value is not None and row.total_value != 0 )): 

                price_str = "Цена, руб./{0}.".format(unit)
                vol_str = "Объём, {0}".format(unit)
                # Если завода еще нет в словаре, добавляем ее
                if factory_name not in factories:
                    factories[factory_name] = {
                        "Выручка, млн. руб.": {},
                        price_str: {},
                        vol_str: {}
                    } 
                # Заполняем данные для каждого показателя 
                if row.total_cost is not None:
                    factories[factory_name]["Выручка, млн. руб."][type_name] = round_to_significant(row.total_cost)
                else:
                    factories[factory_name]["Выручка, млн. руб."][type_name] = 0.0
                if row.cost is not None:
                    factories[factory_name][price_str][type_name] = round_to_significant(row.cost)
                else:
                    factories[factory_name][price_str][type_name] = 0.0
                if row.total_value is not None:
                    factories[factory_name][vol_str][type_name] = round_to_significant(row.total_value)
                else:
                    factories[factory_name][vol_str][type_name] = 0.0

        # Преобразуем в конечный формат
        result = []
        for factory_name, indicators in factories.items():
            revenue_data = []
            for field_name, values in indicators.items():
                field_data = {
                    "field": field_name,
                    "data": [{"type": k, "value": v} for k, v in values.items()]
                }
                revenue_data.append(field_data)
            
            result.append({
                "factoryName": factory_name,
                "revenue": revenue_data
            })

        return {'data': result}


    def get_waterfall(self, year, months, basises=None, products=None, category_product=None):
        return self._balance_view(year, months, basises, products, category_product).waterfall()[0]['data']['data']
