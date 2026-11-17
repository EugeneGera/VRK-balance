from collections import defaultdict
from typing import Dict, List, Optional, Union
from sqlalchemy.orm import scoped_session

from app.entities.schemas import SankeyDataSchema, SankeySingularFlowSchema, StockDetailsSchema, WaterfallDataSchema, WaterfallSchema, products_list_schema, basises_list_schema, category_products_list_schema
from app.repositories.dict_repositories import ProductDictRepository, ShippingBasisDictRepository, UnitDictRepository, ProductCategoryDictRepository
from app.repositories.shipments_repository import ShipmentsRepository
from app.utils import MONTHS, round_to_significant, safe_none_sum, safe_percent, none_to_zero, zero_to_none
from app.services.utils import FilterSessionService
from app.entities.models import ProductDictModel, ShippingBasisDictModel


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


    def _normalize_products(
        self,
        year: int,
        months: List[int],
        basises: Optional[List[str]],
        products: Optional[Union[List[str], str]],
        category_product: Optional[Union[List[str], str]],
    ) -> Optional[Union[List[str], str]]:
        # продукт не выбран, но категория выбрана
        if self._is_empty_filter(products) and not self._is_empty_filter(category_product):
            allowed = self.shipments_repository.get_products_with_resource(
                year=year,
                months=months,
                category_names=category_product,
                basis_names=basises,
            )
            # если ничего не нашли – оставляем как есть, вернётся пустой набор
            if allowed:
                return allowed
        return products

    def update_product_filter(self, year: int, months: List[int], basis_names: List[str],
                              product_names: Optional[Union[List[str], str]] = None,
                              category_names: Optional[Union[List[str], str]] = None):
        updated_filters = FilterSessionService.update_product_filter(session=self.session,
                                                                     year=year, months=months,
                                                                     basis_names=basis_names,
                                                                     product_names=product_names,
                                                                     category_names=category_names)
        # updated_filters = FilterSessionService.get_filters()
        self.product_ids = updated_filters.get('product_ids', None)
        self.product_names = updated_filters.get('product_names', None)
        self.unit_names = updated_filters.get('unit_names', None)
        self.category_names = updated_filters.get('category_names', None)
        
    @staticmethod
    def _is_empty_filter(v):
        if v is None:
            return True
        if isinstance(v, (list, tuple, set)):
            return len([x for x in v if x not in (None, '')]) == 0
        if isinstance(v, str):
            return v.strip() == ''
        return False

    def _no_product_filters(self, products, category_product):
        return self._is_empty_filter(products) and self._is_empty_filter(category_product)
    
    def get_shipped_unit_names(self, year: int, months: List[int],
                               products: Optional[Union[List[str], str]] = None,
                               category_product: Optional[Union[List[str], str]] = None, 
                               basises: Optional[List[str]] = None):
        names = self.shipments_repository.get_shipped_unit_names(year=year,
                                                        months=months,
                                                        basis_names=basises,
                                                        product_names=products,
                                                        category_names=category_product)
        if names is not None and len(names) != 0:
            return names[0][0]

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

    def get_sankey_data(self, year: int,
                        months: List[int],
                        basises: Optional[List[str]] = None,
                        products: Optional[Union[List[str], str]] = None,
                        category_product: Optional[Union[List[str], str]] = None,
                        grouping_base: Optional[str] = None):
        self.update_product_filter(product_names=products,
                                   category_names=category_product,
                                   year=year,
                                   months=months,
                                   basis_names=basises)
            
        if self._no_product_filters(products, category_product):
            return SankeyDataSchema().dump({
                'data': [],
                'products': None,
                'trans_dirs': []
            })

        kind_str = 'заводы' if grouping_base == 'factories' else 'продукты'
        if grouping_base == 'factories':
            grouping_base = ShippingBasisDictModel.name
        elif grouping_base == 'products':
            grouping_base = ProductDictModel.name
        else:
            raise ValueError('Incorrect query parameter value')

        shipments = self.shipments_repository.get_shipments_grouped_by_base(
            product_names=self.product_names,
            category_names=self.category_names,
            year=year,
            months=months,
            basis_names=basises,
            grouping_base=grouping_base)

        if shipments is None or len(shipments) == 0:
            # print('here')
            return SankeyDataSchema().dump({
                'product': self.product_names
            })
        sankey_data_flows = []
        # current_grouping_base = None if shipments is None or len(shipments) == 0 else shipments[0].base
        # total_volume_left = None
        trans_directions = set()
        for shipment in shipments:
            trans_directions.add(shipment.trans_dir)
            # if shipment.base != current_grouping_base:
            #     self._add_unallocated_flow(basis=current_grouping_base, volume=total_volume_left, sankey_flows=sankey_data_flows, kind=kind_str)
                
                # total_volume_left = None
            # if shipment.trans_dir is not None:
            #     total_volume_left = shipment.after_deal_resource
            

            sankey_data_flows.append(SankeySingularFlowSchema().load({
                                        'source': shipment.base,
                                        'target': shipment.trans_dir,
                                        'value': shipment.total_value,
                                        'kind': kind_str,
                                        'price': shipment.cost,
                                        'unit': shipment.unit,
                                        # 'volume_left': None if shipment.after_deal_resource is None else max(shipment.after_deal_resource, 0)
                                    }))
            
            # current_grouping_base = shipment.base

        # self._add_unallocated_flow(basis=shipments[-1].base, volume=total_volume_left, sankey_flows=sankey_data_flows, kind=kind_str)

        
        needs = self.shipments_repository.get_shipments_grouped_by_deal_category(product_names=self.product_names,
                                                                                 year=year,
                                                                                 months=months,
                                                                                 basis_names=basises,
                                                                                 category_names=self.category_names,
                                                                                 )
        
        for need in needs:
            sankey_data_flows.append(SankeySingularFlowSchema().load({
                                        'source': need.trans_dir,
                                        'target': need.deal_category, #need.deal_type if need.deal_type != 'Прочие' else '{0}. {1}'.format(need.deal_type, need.deal_category), # ! hardcore но не hallelujah((
                                        'value': need.total_value,
                                        'volume_left': need.applications_left,
                                        'price': need.cost,
                                        # 'target_kind': need.deal_category, # if need.deal_category is not None else need.deal_type,
                                        'unit': need.unit,
                                        'kind': 'направления сбыта',
                                        'shipping_basis': need.shipping_basis
                                    }))
        
        return SankeyDataSchema().dump({
                'data': sankey_data_flows,
                'products': self.product_names,
                'trans_dirs': list(trans_directions)
            })
            
    def get_stock_details(self, 
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
        
        if self._no_product_filters(products, category_product):
            return StockDetailsSchema().dump({
                'percent': [],
                'absolute': []
            })

        data = self.shipments_repository.get_stock_details(year=year,
                                                                  months=months,
                                                                  basis_names=basises,
                                                                  product_names=self.product_names,
                                                                  category_names=self.category_names)
        transformed = { 
                        'percent': [],
                        'absolute': []
                      }
        
        for row in data:
            month_key = row.month
            # try:
            #     month_key = int(month_key)
            #     month_name = MONTHS[month_key - 1]
            # except Exception:
            #     continue
            
            base_category_str = 'Реализация'
            full_stock_str = 'Реализация на бирже'
            stock_necessary_str = 'Биржа обязательства'
            stock_additional_str = 'Биржа доп. объёмы'
            non_stock_str = 'Внебиржевая реализация'
            stock_sum_val = safe_none_sum(row.stock_necessary, row.stock_additional)
            full_val = safe_none_sum(stock_sum_val, row.non_stock)

            transformed['absolute'].append({
                "month": month_key,
                "data": [
                            {
                                'type': full_stock_str,
                                'value': stock_sum_val,
                                'category': base_category_str
                            },
                            {
                                'type': stock_necessary_str,
                                'value': row.stock_necessary,
                                'category': full_stock_str
                            },
                            {
                                'type': stock_additional_str,
                                'value': row.stock_additional,
                                'category': full_stock_str
                            },
                            {
                                'type': non_stock_str,
                                'value': row.non_stock,
                                'category': base_category_str
                            }
                        ]
            })
            transformed['percent'].append({
                "month": month_key,
                "data": [
                            {
                                'type': full_stock_str,
                                'value': safe_percent(stock_sum_val, full_val),
                                'category': base_category_str
                                },
                            {
                                'type': stock_necessary_str,
                                'value': safe_percent(row.stock_necessary, full_val),
                                'category': full_stock_str
                            },
                            {
                                'type': stock_additional_str,
                                'value': safe_percent(row.stock_additional, full_val),
                                'category': full_stock_str
                            },
                            {
                                'type': non_stock_str,
                                'value': safe_percent(row.non_stock, full_val),
                                'category': base_category_str
                            }
                        ]
            })
        return StockDetailsSchema().dump(transformed)




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

    def _update_rows_dict(self, rows_dict: Dict, key: str, row_values: List, month_key: int = 0):
        rows_dict[key] = [round_to_significant(safe_none_sum(
            x, y)) for x, y in zip(rows_dict[key][:-1], row_values)] + [month_key]
        # print(rows_dict[key])

    def _sort_dict_of_lists_by_last_value(self, input_dict: Dict[str, List]):
    
        from collections import OrderedDict
    
        sorted_items = sorted(input_dict.items(), key=lambda item: item[1][-1])
        
        result = OrderedDict()
        for key, value_list in sorted_items:
            result[key] = value_list
        
        return result

    def get_table(self,
              year: int,
              months: List[int],
              basises: Optional[List[str]] = None,
              products: Optional[Union[List[str], str]] = None,
              category_product: Optional[Union[List[str], str]] = None):

        products = self._normalize_products(
            year=year,
            months=months,
            basises=basises,
            products=products,
            category_product=category_product,
        )

        self.update_product_filter(
            product_names=products,
            year=year,
            months=months,
            basis_names=basises,
            category_names=category_product,
        )

    
        def _empty(v):
            if v is None:
                return True
            if isinstance(v, (list, tuple, set)):
                return len([x for x in v if x not in (None, '')]) == 0
            if isinstance(v, str):
                return v.strip() == ''
            return False
            
        if _empty(products) and _empty(category_product):
            return []

        additional_months = []
        additional_months_sum_name = None

        if len(months) == 1:
            base = months[0]

            for step in (1, 2):
                nm = base + step
                if 1 <= nm <= 12:
                    additional_months.append(nm)

            if len(additional_months) == 2:
                additional_months_names = f"{MONTHS[additional_months[0]-1].lower()}-{MONTHS[additional_months[1]-1].lower()}"
                additional_months_sum_name = f"Итого {additional_months_names}"
            elif len(additional_months) == 1:
                additional_months_names = MONTHS[additional_months[0]-1].lower()
                additional_months_sum_name = f"Итого {additional_months_names}"

    # Добавление обработки ошибок для запроса к базе данных
        try:
            table_data_rows = self.shipments_repository.get_table_data(
                year=year,
                months=(months + additional_months),
                basis_names=basises,
                product_names=self.product_names,
                category_names=self.category_names
            )
            
            # Если данные не получены, возвращаем пустой список
            if not table_data_rows:
                return []

        except Exception as e:
            # Логируем ошибку, если нужно, и возвращаем пустой список
            print(f"Error fetching data from database: {e}")
            return []

        result_all_by_basis = defaultdict(lambda: (list([0] * (len(table_data_rows[0]) - 2) + [0])))
        result_sum_by_month = defaultdict(lambda: list([0] * (len(table_data_rows[0]) - 1)))
        result_factory_sum = defaultdict(lambda: list([0] * (len(table_data_rows[0]) - 1)))

        for row in table_data_rows:
            factory_key = row[0]
            month_key = row[-1]

            try:
                month_key = int(month_key)
            except Exception:
                continue
            try:
                month_name = MONTHS[month_key - 1]
            except IndexError:
                continue

            row_values = list(row[1:-1])

            # Если нужно, добавим обработку ошибок для логики с month_key в дополнительном месяце
            if month_key in additional_months:
                month_factory_sum_name = f'Итого {additional_months_names} ({str(factory_key)})'
                self._update_rows_dict(result_factory_sum, month_factory_sum_name, row_values, month_key)
                self._update_rows_dict(result_sum_by_month, additional_months_sum_name, row_values, month_key)
            else:
                month_sum_name = f'Итого {month_name.lower()}'
                month_factory_sum_name = f'Итого {month_name.lower()} ({str(factory_key)})'

                self._update_rows_dict(result_all_by_basis, str(factory_key), row_values)
                self._update_rows_dict(result_factory_sum, month_factory_sum_name, row_values, month_key)
                self._update_rows_dict(result_sum_by_month, month_sum_name, row_values, month_key)

            self._update_rows_dict(result_sum_by_month, 'Итого', row_values, month_key)

    # Обработка ошибок для сортировки результатов, если необходимо
        try:
            result_factory_sum = self._sort_dict_of_lists_by_last_value(result_factory_sum)
            result_sum_by_month = self._sort_dict_of_lists_by_last_value(result_sum_by_month)
        except Exception as e:
            print(f"Error sorting data: {e}")
            return []

        data_list = [[key] + result_all_by_basis[key][:-1] for key in result_all_by_basis.keys()]
        factory_sum_list = [[key] + result_factory_sum[key][:-1] for key in result_factory_sum.keys()]
        factory_totals = [0.0] * (len(table_data_rows[0]) - 2)

        for factory_key, agg_vals in result_all_by_basis.items():
            vals = agg_vals[:-1]
            factory_totals = [x + y for x, y in zip(factory_totals, vals)]

        grand_total_row = ['Итого'] + factory_totals

        ordered_list = []
        for data_entry in data_list:
            factory_key = data_entry[0]
            ordered_list.append(data_entry)

            matching_sums = [
                entry for entry in factory_sum_list 
                if f"({factory_key})" in entry[0]
            ]
            ordered_list.extend(matching_sums)

        ordered_list.append(grand_total_row)

        return ordered_list

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


    def get_waterfall(self,
                     year: int,
                     months: List[int],
                     basises: Optional[List[str]] = None,
                     products: Optional[Union[List[str], str]] = None,
                     category_product: Optional[Union[List[str], str]] = None):

        products = self._normalize_products(
            year=year,
            months=months,
            basises=basises,
            products=products,
            category_product=category_product,
        )

        self.update_product_filter(
            product_names=products,
            year=year,
            months=months,
            basis_names=basises,
            category_names=category_product,
        )

        if self._no_product_filters(products, category_product):
            return []

        data = self.shipments_repository.get_waterfall_data(
            product_names=self.product_names,
            category_names=self.category_names,
            year=year,
            months=months,
            basis_names=basises,
        )

        print(data)
        waterfall_data = []
        total_waterfall = defaultdict(lambda: defaultdict(None))
        # print(total_waterfall)
        stock_keys = ['Внутренний рынок', 'Экспорт', 'Нужды ДО']
        for name in stock_keys:
            total_waterfall['distribution'][name] = {'value': None}

        for row in data:
            print(row)
            row = dict(row._mapping)
            row['inner_value'] = max(0, row['inner_value']) if row['inner_value'] else None
            row['export_value'] = max(0, row['export_value']) if row['export_value'] else None
            row['needs_value'] = max(0, row['needs_value']) if row['needs_value'] else None
            row['add_need'] = max(0, row['add_need']) if row['add_need'] else None

            total_waterfall['total']['plan'] = safe_none_sum(total_waterfall['total'].get('plan'), row['total_plan'])
            total_waterfall['total']['leftovers'] = safe_none_sum(total_waterfall['total'].get('leftovers'), row['total_leftovers'])
            total_waterfall['available_resource']['available'] = safe_none_sum(total_waterfall['available_resource'].get('available'), row['available_available'])
            total_waterfall['available_resource']['restrictions'] = safe_none_sum(total_waterfall['available_resource'].get('restrictions'), row['available_restriction'])
            
            total_waterfall['distribution']['Внутренний рынок']['value'] = safe_none_sum(total_waterfall['distribution']['Внутренний рынок'].get('value'), row['inner_value'])
            total_waterfall['distribution']['Внутренний рынок']['claim'] = safe_none_sum(total_waterfall['distribution']['Внутренний рынок'].get('claim'), row['inner_claim'])

            total_waterfall['distribution']['Экспорт']['value'] = safe_none_sum(total_waterfall['distribution']['Экспорт'].get('value'), row['export_value'])
            total_waterfall['distribution']['Экспорт']['claim'] = safe_none_sum(total_waterfall['distribution']['Экспорт'].get('claim'), row['export_claim'])

            total_waterfall['distribution']['Нужды ДО']['value'] = safe_none_sum(total_waterfall['distribution']['Нужды ДО'].get('value'), row['needs_value'])
            total_waterfall['distribution']['Нужды ДО']['claim'] = safe_none_sum(total_waterfall['distribution']['Нужды ДО'].get('claim'), row['needs_claim'])

            total_waterfall['resource_leftover']['leftovers'] = safe_none_sum(total_waterfall['resource_leftover'].get('leftovers'), row['leftovers'])
            total_waterfall['need']['need'] = safe_none_sum(total_waterfall['need'].get('need'), row['add_need'])

            # total_waterfall.available_restriction.available = safe_none_sum()

            waterfall_data.append(
                WaterfallSchema().dump({
                    "name": row['shipping_basis'],
                    "data": {
                        "total": {
                            "plan": row['total_plan'],
                            "leftovers": row['total_leftovers']
                        },
                        "available_resource": {
                            "available": row['available_available'],
                            "restrictions": row['available_restriction']
                        },
                        "distribution": [
                            {
                                "name": 'Внутренний рынок',
                                "value": row['inner_value'],
                                "claim": row['inner_claim']
                            },
                            {
                                "name": 'Экспорт',
                                "value": row['export_value'],
                                "claim": row['export_claim']
                            },
                            {
                                "name": 'Нужды ДО',
                                "value": row['needs_value'],
                                "claim": row['needs_claim']
                            }
                        ],
                        "resource_leftover": {'leftovers': row['leftovers']},
                        'need': {'need': row['add_need']}
                    }
                })
            )

        try:
            table_rows = self.shipments_repository.get_table_data(
                year=year,
                months=months,
                basis_names=basises,
                product_names=self.product_names,
                category_names=self.category_names,
            )

            total_plan_from_table = 0
            total_leftovers_from_table = 0
            total_resource_from_table = 0

            for r in table_rows:
                # r: basis_name, leftovers, production_plan, resource_for_distribution, ..., month
                total_leftovers_from_table = safe_none_sum(
                    total_leftovers_from_table,
                    getattr(r, 'leftovers', None),
                )
                total_plan_from_table = safe_none_sum(
                    total_plan_from_table,
                    getattr(r, 'production_plan', None),
                )
                total_resource_from_table = safe_none_sum(
                    total_resource_from_table,
                    getattr(r, 'resource_for_distribution', None),
                )

            total_waterfall['total']['leftovers'] = total_leftovers_from_table
            total_waterfall['total']['plan'] = total_plan_from_table
            total_waterfall['available_resource']['available'] = total_resource_from_table
        except Exception as e:
            print('Failed to sync waterfall totals with table_data:', e)

        modified_distribution = []
        for name, sub_dict in total_waterfall['distribution'].items():
            new_dict = {"name": name}
            new_dict.update(sub_dict)
            modified_distribution.append(new_dict)
        total_waterfall['distribution'] = modified_distribution

        waterfall_data.append(WaterfallSchema().dump({"data": dict(total_waterfall)}))
        return waterfall_data
