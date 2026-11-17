from typing import List, Optional, Union
from sqlalchemy import Column, select, func, and_, or_, case
from sqlalchemy.orm import scoped_session

from app.repositories.repository import BaseRepository
from app.entities.models import AllResourceModel, DealCategoryDictModel, DistrChannelDictModel, ProductDictModel, ProductionPlanModel, ShipmentsModel, ShippingBasisDictModel, TransApplicationModel, TransDirDictModel, TransportDictModel, UnitDictModel, ProductCategoryDictModel
from app.repositories.mixins import DictsFilterMixin, ShipmentsFilterMixin, DateFilterMixin
from app.repositories.utils import (GOZ_DEAL_CAT_CASE, INNER_TRANS_DIR_CASE, 
                                    EXPORT_TRANS_DIR_CASE, RETAIL_OPT_DEAL_CAT_CASE, 
                                    STOCK_EXCESS_DEAL_CAT_CASE, STOCK_STATE_NECESSARY_DEAL_CAT_CASE, WHOLESALE_DEAL_CAT_CASE, 
                                    LONG_TERM_DEAL_CAT_CASE, 
                                    OTHER_DEAL_CAT_CASE,
                                    NEEDS_TRANS_DIR_CASE,
                                    FRAME_AGREEMENT_DEAL_CAT_CASE,
                                    ensure_list)

class ShipmentsRepository(BaseRepository, DateFilterMixin, ShipmentsFilterMixin, DictsFilterMixin):
    def __init__(self, session: scoped_session):
        self.session = session

    def get_latest_period(self):
        return (
            self.session.query(
                ShipmentsModel.year,
                ShipmentsModel.month,
                ProductCategoryDictModel.name.label('category_product'),
            )
            .select_from(ShipmentsModel)
            .join(ProductCategoryDictModel, ProductCategoryDictModel.id == ShipmentsModel.product_category_id)
            .join(ProductDictModel, ProductDictModel.id == ShipmentsModel.product_id)
            .filter(
                ShipmentsModel.year > 0,
                ShipmentsModel.month.between(1, 12),
                ProductCategoryDictModel.name.isnot(None),
                ProductCategoryDictModel.name.notin_(['', '0']),
                or_(
                    ShipmentsModel.value > 0,
                    ShipmentsModel.all_resource > 0,
                    ShipmentsModel.plan > 0,
                    ShipmentsModel.leftovers > 0,
                ),
            )
            .order_by(ShipmentsModel.year.desc(), ShipmentsModel.month.desc(), ProductCategoryDictModel.id.asc())
            .first()
        )

    def get_products_with_resource(
        self,
        year: int,
        months: Union[int, List[int]],
        category_names: Optional[Union[str, List[str]]] = None,
        basis_names: Optional[List[str]] = None,
    ) -> List[str]:
        q = self.session.query(ProductDictModel.name).select_from(AllResourceModel)

        # join product
        q = q.join(ProductDictModel, ProductDictModel.id == AllResourceModel.product_id)

        # фильтр по дате
        q = self.filter_by_date(query=q, model=AllResourceModel, year=year, months=months)

        # фильтр по категории продукта
        q = self.filter_by_dict_names(
            query=q,
            dict_model=ProductCategoryDictModel,
            dict_names=category_names,
            join_condition=(ProductDictModel.product_category_id == ProductCategoryDictModel.id),
        )

        # фильтр по базисам (если есть)
        q = self.filter_by_dict_names(
            query=q,
            dict_model=ShippingBasisDictModel,
            dict_names=basis_names,
            join_condition=(ShippingBasisDictModel.id == AllResourceModel.shipping_basis_id),
        )

        q = q.distinct().order_by(ProductDictModel.name)
        return [row[0] for row in q.all()]

    def get_shipped_product(self, year: int, months: Union[int, List[int]],
                            basis_names: List[str] = None,
                            category_names: List[str] = None,
                            *args, **kwargs) -> Optional[List[int]]:
        query = self.session.query(ShipmentsModel).with_entities(ShipmentsModel.product_id).filter(*args).filter_by(**kwargs)
        query = self.filter_by_date(query, model=ShipmentsModel, year=year, months=months)
        query = self.filter_by_dict_names(query, dict_model=ShippingBasisDictModel, dict_names=basis_names)
        query = self.filter_by_dict_names(query, dict_model=ProductCategoryDictModel, dict_names=category_names)


        shipments = query.distinct().all()
        if shipments is not None:
            return [shipment.product_id for shipment in shipments]
        
    def get_shipped_unit_names(self, year: int, months: Union[int, List[int]],
                               basis_names: List[str] = None,
                               product_names: List[str] = None,
                               category_names: List[str] = None,
                               *args, **kwargs) -> Optional[List[int]]:
        query = self.session.query(ShipmentsModel, UnitDictModel).with_entities(UnitDictModel.name).select_from(ShipmentsModel).join(UnitDictModel, UnitDictModel.id==ShipmentsModel.unit_id)#.filter(*args).filter_by(**kwargs)
        query = self.filter_by_date(query, model=ShipmentsModel, year=year, months=months)
        query = self.filter_by_dict_names(query, dict_model=ProductDictModel, dict_names=product_names, join_condition=(ProductDictModel.id==ShipmentsModel.product_id))
        query = self.filter_by_dict_names(query, dict_model=ProductCategoryDictModel, dict_names=category_names, join_condition=(ProductCategoryDictModel.id==ShipmentsModel.product_category_id))
        query = self.filter_by_dict_names(query, dict_model=ShippingBasisDictModel, dict_names=basis_names, join_condition=(ShippingBasisDictModel.id==ShipmentsModel.shipping_basis_id))

        names = query.distinct().all()
        return names
                
    def get_working_basises(self, year: int,
                                  months: Union[int, List[int]],
                                  product_names: List[str] = None,
                                  category_names: Union[str, List[str]] = None,
                                  *args, **kwargs) -> Optional[List[int]]:
        query = self.session.query(ShippingBasisDictModel).filter(*args).filter_by(**kwargs).select_from(ShipmentsModel)
        query = self.filter_by_date(query, model=ShipmentsModel, year=year, months=months)
        query = self.filter_by_dict_names(query, dict_model=ProductDictModel, dict_names=product_names)
        query = self.filter_by_dict_names(query, dict_model=ProductCategoryDictModel, dict_names=category_names)
        query = query.join(ShippingBasisDictModel)
        return query.all()


    # TODO нейминг
    def get_working_products(self, category_names: Union[str, List[str]] = None,
                             *args, **kwargs) -> Optional[List[ProductDictModel]]:
        query = self.session.query(ProductDictModel)

        if category_names:
            if isinstance(category_names, str):
                category_names = [category_names]

            query = query.join(
                ProductCategoryDictModel,
                ProductDictModel.product_category_id == ProductCategoryDictModel.id
            ).filter(
                ProductCategoryDictModel.name.in_(category_names)
            )

        return query.all()
    
    def get_shipped_categories(self, year: int, months: Union[int, List[int]],
                                    basis_names: List[str] = None,
                                    *args, **kwargs) -> Optional[List[int]]:
        query = self.session.query(ShipmentsModel).with_entities(ShipmentsModel.product_category_id).filter(*args).filter_by(**kwargs)
        query = self.filter_by_date(query, model=ShipmentsModel, year=year, months=months)
        query = self.filter_by_dict_names(query, dict_model=ShippingBasisDictModel, dict_names=basis_names)

        shipments = query.all()
        return shipments
        # if shipments is not None:
        #     return [shipment.product_id for shipment in shipments]

    def get_shipments_grouped_by_base(self, 
                                           product_names: Union[str, List[str]],
                                           year: int, 
                                           months: Union[int, List[int]],
                                           basis_names: Union[str, List[str]]=None, 
                                           category_names: Union[str, List[str]]=None,
                                           grouping_base: Column = None,
                                           *args, **kwargs) -> Optional[List[ShipmentsModel]]: # заводы

        if not grouping_base:
            grouping_base = ShippingBasisDictModel.name

        base_cte = (
            self.session.query(
                ShipmentsModel.accepted_deal,
                ShipmentsModel.all_resource,
                ShipmentsModel.cost,
                ShipmentsModel.product_category_id,
                ShipmentsModel.product_id,
                ShipmentsModel.trans_dir_id,
                ShipmentsModel.unit_id,
                ShipmentsModel.month,
                grouping_base.label('base')
            )
            .join(UnitDictModel, UnitDictModel.id == ShipmentsModel.unit_id)
            .filter(*args)
            .filter_by(**kwargs)
            .filter(ShipmentsModel.year == year)
            .filter(ShipmentsModel.month.in_(months if isinstance(months, list) else [months]))
        ) 

        base_cte = self.filter_by_dict_names(query=base_cte, dict_model=ProductCategoryDictModel, dict_names=category_names)
        base_cte = self.filter_by_dict_names(query=base_cte, dict_model=ProductDictModel, dict_names=product_names, join_condition=ProductDictModel.product_category_id==ProductCategoryDictModel.id)
        base_cte = self.filter_by_date(query=base_cte, model=ShipmentsModel, year=year, months=months)
        base_cte = self.filter_by_dict_names(query=base_cte, dict_model=ShippingBasisDictModel, dict_names=basis_names) 

        base_cte = base_cte.cte('base_data')
        
        monthly_max_all_rsrc = self.session.query(
                base_cte.c.month.label('month'),
                base_cte.c.base.label('base'),
                # base_cte.c.trans_dir_id.label('trans_dir_id'),
                func.max(base_cte.c.all_resource).label('all_resource')
            ).group_by(base_cte.c.month, base_cte.c.base).cte('monthly_max_all_rsrc')
        
        
        leftovers_alias_a = (self.session.query(
                monthly_max_all_rsrc.c.base.label('base'),
                #monthly_max_all_rsrc.c.trans_dir_id.label('trans_dir_id'),
                func.sum(monthly_max_all_rsrc.c.all_resource).label('all_resource')
            ).group_by(monthly_max_all_rsrc.c.base)).cte('leftovers_alias_a') # СУММА МАКСИМАЛЬНЫХ ЗА КАЖДЫЙ МЕСЯЦ
        
        leftovers_alias_b = (self.session.query(
                base_cte.c.base.label('base'),
                # base_cte.c.trans_dir_id.label('trans_dir_id'),
                func.sum(base_cte.c.accepted_deal).label('accepted_deal')
            ).group_by(base_cte.c.base)).cte('leftovers_alias_b') # СУММА ПО ВСЕМ МЕСЯЦВМ!!!1111
        
        leftovers_alias = (self.session.query(
                leftovers_alias_a.c.base.label('base'),
                # leftovers_alias_a.c.trans_dir_id.label('trans_dir_id'),
                (leftovers_alias_a.c.all_resource - 
                leftovers_alias_b.c.accepted_deal)
                .label('after_deal_resource')
            ).join(leftovers_alias_b, and_(leftovers_alias_b.c.base == leftovers_alias_a.c.base))).cte('leftovers_alias')
        
        # leftovers = self.session.query(
        #     leftovers_alias.c.base,
        #     # leftovers_alias.c.trans_dir_id,
        #     func.sum(leftovers_alias.c.after_deal_resource).label('after_deal_resource')
        # ).group_by(leftovers_alias.c.base).subquery()

        # Main query
        query = (
            self.session.query(
                base_cte.c.base,
                TransDirDictModel.name.label('trans_dir'),
                UnitDictModel.name.label('unit'),
                func.sum(base_cte.c.cost).label('cost'),
                func.sum(base_cte.c.accepted_deal).label('total_value'),
                # leftovers.c.after_deal_resource
            )
            .select_from(base_cte)
            .join(TransDirDictModel, TransDirDictModel.id == base_cte.c.trans_dir_id)
            .join(UnitDictModel, UnitDictModel.id == base_cte.c.unit_id)
            # .join(leftovers, and_(leftovers.c.base == base_cte.c.base))
            .group_by(
                base_cte.c.base,
                TransDirDictModel.name, 
                UnitDictModel.name,
                # leftovers.c.after_deal_resource
            )
        )#.order_by(leftovers.c.after_deal_resource)

        if product_names:
            names = ensure_list(product_names)
            query = query.join(ProductDictModel, ProductDictModel.id == base_cte.c.product_id)
            query = query.filter(ProductDictModel.name.in_(names))

        if category_names:
            categories = ensure_list(category_names)
            query = query.join(ProductCategoryDictModel, ProductCategoryDictModel.id == base_cte.c.product_category_id)
            query = query.filter(ProductCategoryDictModel.name.in_(categories))

        # print(query.all())
        return query.all()
    
    def get_shipments_grouped_by_deal_category(self, 
                                               product_names: Union[str, List[str]], 
                                               year: int, 
                                               months: Union[int, List[int]],
                                               basis_names=None, 
                                               category_names: Union[str, List[str]]=None,
                                               *args, **kwargs) -> Optional[List[ShipmentsModel]]:
        query = self.session.query(ShipmentsModel,
                                   TransDirDictModel,
                                   UnitDictModel,
                                   DealCategoryDictModel,
                                   ShippingBasisDictModel
                            ).with_entities(
                                   func.sum(ShipmentsModel.accepted_deal).label('total_value'),
                                   TransDirDictModel.name.label('trans_dir'),
                                   func.sum(ShipmentsModel.left_resource).label('applications_left'),
                                   UnitDictModel.name.label('unit'),
                                   func.sum(ShipmentsModel.cost).label('cost'),
                                   DealCategoryDictModel.name.label('deal_category'),
                                   ShippingBasisDictModel.name.label('shipping_basis')
                            ).filter(*args).filter_by(**kwargs)
        
        query = query.join(TransDirDictModel, TransDirDictModel.id == ShipmentsModel.trans_dir_id
                    ).join(DealCategoryDictModel
                    ).join(UnitDictModel)
        
        query = self.filter_by_dict_names(query=query, dict_model=ProductCategoryDictModel, dict_names=category_names)
        query = self.filter_by_dict_names(query=query, dict_model=ProductDictModel, dict_names=product_names, join_condition=ProductDictModel.product_category_id==ProductCategoryDictModel.id)
        query = self.filter_by_date(query=query, model=ShipmentsModel, year=year, months=months)
        query = self.filter_by_dict_names(query=query, dict_model=ShippingBasisDictModel, dict_names=basis_names)

        # if category_names:
        
        query = query.group_by(
            TransDirDictModel.name, #ShipmentsModel.trans_dir_id,
            UnitDictModel.name, #ShipmentsModel.unit_id,
            DealCategoryDictModel.name,
            ShippingBasisDictModel.name
        )
        return query.all()

    def get_stock_details(self, 
                          year: int, 
                          months: Union[int, List[int]], 
                          product_names: Union[str, List[str]], 
                          category_names: Union[str, List[str]]=None,
                          basis_names: List[str]=None,
                          *args, **kwargs) -> Optional[List[ShipmentsModel]]:
        query = self.session.query(
            ShipmentsModel,
        ).with_entities(
            func.sum(
                    case(((STOCK_STATE_NECESSARY_DEAL_CAT_CASE(ShipmentsModel)),
                            ShipmentsModel.accepted_deal
                         ), else_=None)
                    ).label('stock_necessary'),
            func.sum(
                    case(((STOCK_EXCESS_DEAL_CAT_CASE(ShipmentsModel)), 
                            ShipmentsModel.accepted_deal
                         ), else_=None)
                    ).label('stock_additional'),
            (func.sum(ShipmentsModel.accepted_deal) - func.sum(ShipmentsModel.value_exchange)).label('non_stock'),
            ShipmentsModel.month,
        ).order_by(ShipmentsModel.month).filter(*args).filter_by(**kwargs)

        query = query.join(DistrChannelDictModel)

        query = self.filter_by_dict_names(query=query, dict_model=ProductDictModel, dict_names=product_names)
        query = self.filter_by_date(query=query, model=ShipmentsModel, year=year, months=months)
        query = self.filter_by_dict_names(query=query, dict_model=ShippingBasisDictModel, dict_names=basis_names)
        query = self.filter_by_dict_names(query=query, dict_model=ProductCategoryDictModel, dict_names=category_names)
        query = query.group_by(
            # DistrChannelDictModel.name,
            ShipmentsModel.month,
        )
        # print(query.all())
        return query.all()
    
    def get_factory_leftovers(self,
                                year: int,
                                months: Union[int, List[int]],
                                product_names: Union[str, List[str]],
                                basis_names: List[str] = None,
                                category_names: Union[str, List[str]] = None,
                                *args, **kwargs) -> Optional[List[ShipmentsModel]]:
            # # Преобразуем параметры к спискам
            
            # months = ensure_list(months)
            # product_names = ensure_list(product_names)
            # basis_names = ensure_list(basis_names)
            # category_names = ensure_list(category_names)

            # where_conditions = [
            #     ShipmentsModel.year == year,
            #     ShipmentsModel.month.in_(months),
            # ]

            # if basis_names is not None:
            #     where_conditions.append(ShippingBasisDictModel.name.in_(basis_names))

            # if category_names is not None:
            #     where_conditions.append(ProductCategoryDictModel.name.in_(category_names))

            # if product_names is not None:
            #     where_conditions.append(ProductDictModel.name.in_(product_names))

            # Подзапрос, который высчитывает дельту и заявки на реализацию по месяцам:
            #.label("all_resource"))
            delta_zayav = (
                self.session.query(
                    ShippingBasisDictModel.name.label("factory_name"),
                    ShipmentsModel.month,
                    case((func.sum(TransApplicationModel.value) == None,
                                func.max(ShipmentsModel.all_resource),
                                ),
                        (func.max(ShipmentsModel.all_resource) == None,
                        -func.sum(TransApplicationModel.value),
                        ),
                        else_=(func.max(ShipmentsModel.all_resource) - func.sum(TransApplicationModel.value))
                    ).label("delta"),
                    case((
                        func.sum(TransApplicationModel.value) == None,
                        0,
                    ),
                        else_=func.sum(TransApplicationModel.value)
                    ).label("applications"),
                    case((
                        func.max(ShipmentsModel.all_resource) == None,
                        0,
                    ),
                        else_=func.max(ShipmentsModel.all_resource)
                    ).label("all_resource")
                ).select_from(ShipmentsModel)
                .outerjoin(
                    TransApplicationModel,
                    (TransApplicationModel.id == ShipmentsModel.trans_application_id)
                    & (ShipmentsModel.month == TransApplicationModel.month)
                    & (ShipmentsModel.year == TransApplicationModel.year)
                    & (ShipmentsModel.shipping_basis_id == TransApplicationModel.shipping_basis_id)
                    & (ShipmentsModel.product_id == TransApplicationModel.product_id)
                ))
                # .where(*where_conditions)
            delta_zayav = self.filter_by_dict_names(query=delta_zayav, dict_model=ProductDictModel, dict_names=product_names, join_condition=ShipmentsModel.product_id==ProductDictModel.id)
            delta_zayav = self.filter_by_date(query=delta_zayav, model=ShipmentsModel, year=year, months=months)
            delta_zayav = self.filter_by_dict_names(query=delta_zayav, dict_model=ShippingBasisDictModel, dict_names=basis_names, join_condition=ShippingBasisDictModel.id==ShipmentsModel.shipping_basis_id)
            delta_zayav = self.filter_by_dict_names(query=delta_zayav, dict_model=ProductCategoryDictModel, dict_names=category_names, join_condition=ShipmentsModel.product_category_id==ProductCategoryDictModel.id) 
            delta_zayav = delta_zayav.group_by(ShippingBasisDictModel.name, ShipmentsModel.month)
            delta_zayav = delta_zayav.subquery("delta_zayav")
            
            # максимум ресурса по каждому собственнику в рамках (basis_id, month)
            owner_resource_q = (
                self.session.query(
                    ShipmentsModel.shipping_basis_id.label('basis_id'),
                    ShipmentsModel.month.label('month'),
                    ShipmentsModel.product_owner_id.label('product_owner_id'),
                    func.max(ShipmentsModel.all_resource).label('owner_max_resource'),
                )
                .select_from(ShipmentsModel)
            )

            owner_resource_q = self.filter_by_dict_names(
                query=owner_resource_q,
                dict_model=ProductDictModel,
                dict_names=product_names,
            )
            owner_resource_q = self.filter_by_date(
                query=owner_resource_q,
                model=ShipmentsModel,
                year=year,
                months=months,
            )
            owner_resource_q = self.filter_by_dict_names(
                query=owner_resource_q,
                dict_model=ShippingBasisDictModel,
                dict_names=basis_names,
            )
            owner_resource_q = self.filter_by_dict_names(
                query=owner_resource_q,
                dict_model=ProductCategoryDictModel,
                dict_names=category_names,
            )

            owner_resource_q = owner_resource_q.group_by(
                ShipmentsModel.shipping_basis_id,
                ShipmentsModel.month,
                ShipmentsModel.product_owner_id,
            )

            owner_resource_subq = owner_resource_q.subquery('owner_resource')

            # Сумма максимумов по собственникам в разрезе (basis_id, month)
            owner_resource_sum_q = (
                self.session.query(
                    owner_resource_subq.c.basis_id,
                    owner_resource_subq.c.month,
                    func.sum(owner_resource_subq.c.owner_max_resource)
                        .label('resource_for_distribution_by_owners'),
                )
                .group_by(
                    owner_resource_subq.c.basis_id,
                    owner_resource_subq.c.month,
                )
            )
            owner_resource_sum_subq = owner_resource_sum_q.subquery('owner_resource_by_basis_month')

            # Агрегация по заводам (имя завода)
            resource_by_factory_q = (
                self.session.query(
                    ShippingBasisDictModel.name.label('factory_name'),
                    func.sum(owner_resource_sum_subq.c.resource_for_distribution_by_owners)
                        .label('all_resource'),
                )
                .join(ShippingBasisDictModel,
                      ShippingBasisDictModel.id == owner_resource_sum_subq.c.basis_id)
                .group_by(ShippingBasisDictModel.name)
            )
            resource_by_factory_subq = resource_by_factory_q.subquery('resource_by_factory')

            plan_conditions = [
                ProductionPlanModel.year == year,
                ProductionPlanModel.month.in_(months),
            ]

            if basis_names is not None:
                plan_conditions.append(ShippingBasisDictModel.name.in_(basis_names))

            if category_names is not None:
                plan_conditions.append(ProductCategoryDictModel.name.in_(category_names))

            if product_names is not None:
                plan_conditions.append(ProductDictModel.name.in_(product_names))
            # Подзапрос для План производства:
            plan = (
                select(
                    ShippingBasisDictModel.name.label("factory_name"),
                    ProductionPlanModel.month,
                    func.sum(ProductionPlanModel.left).label("left"),
                    func.sum(ProductionPlanModel.plan).label("plan"),
                    (func.sum(ProductionPlanModel.max_shipment) + func.sum(ProductionPlanModel.min_left)).label("restrictions"),
                )
                .join(ProductDictModel, ProductDictModel.id == ProductionPlanModel.product_id)
                .join(ShippingBasisDictModel, ShippingBasisDictModel.id == ProductionPlanModel.shipping_basis_id)
                .join(ProductCategoryDictModel, ProductCategoryDictModel.id == ProductDictModel.product_category_id)
                .where(*plan_conditions)
                .group_by(ShippingBasisDictModel.name, ProductionPlanModel.month)
                .subquery("plan")
            )

            # print(plan.selectable.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))

            # # Подзапрос для максимального all_resource по заводу
            # max_all_resource = (
            #     select(
            #         delta_zayav.c.factory_name,
            #         func.max(delta_zayav.c.all_resource).label("max_all_resource")
            #     )
            #     .group_by(delta_zayav.c.factory_name, delta_zayav.c.month)
            #     .subquery("max_all_resource")
            # )

            query = (
                self.session.query(
                    delta_zayav.c.factory_name.label("factory_name"),
                    func.coalesce(func.sum(plan.c.left), 0).label("left"),
                    func.coalesce(func.sum(plan.c.plan), 0).label("plan"),
                    func.coalesce(func.sum(delta_zayav.c.delta), 0).label("delta"),
                    func.coalesce(func.sum(delta_zayav.c.applications), 0).label("applications"),
                    func.coalesce(func.sum(plan.c.restrictions), 0).label("restrictions"),
                    func.max(resource_by_factory_subq.c.all_resource).label("all_resource"),
                )
                .outerjoin(
                    plan,
                    (delta_zayav.c.factory_name == plan.c.factory_name)
                    & (delta_zayav.c.month == plan.c.month)
                )
                .outerjoin(
                    resource_by_factory_subq,
                    resource_by_factory_subq.c.factory_name == delta_zayav.c.factory_name,
                )
                .group_by(delta_zayav.c.factory_name)
            )

            return query.all()
    

    def get_table_data(self, 
                       year: int, 
                       months: Union[int, List[int]], 
                       product_names: Union[str, List[str]],
                       category_names: Union[str, List[str]],
                       basis_names: List[str]=None,
                       *args, **kwargs) -> Optional[List[ShipmentsModel]]:
        q = self.session.query(
                ProductionPlanModel.month,
                ShippingBasisDictModel.id.label('basis_id'),
                func.sum(ProductionPlanModel.value_exchange).label('all_stocks_inner'),      # Всего биржа (Внутренний рынок)
                func.sum(ProductionPlanModel.left).label('leftovers'),                       # Остатки
                func.sum(ProductionPlanModel.plan).label('production_plan'),                 # План производства
            ).select_from(ProductionPlanModel)
        q = self.filter_by_dict_names(query=q, dict_model=ProductDictModel, dict_names=product_names, join_condition=ProductDictModel.id==ProductionPlanModel.product_id)
        q = self.filter_by_dict_names(query=q, dict_model=ProductCategoryDictModel, dict_names=category_names, join_condition=ProductDictModel.product_category_id==ProductCategoryDictModel.id)
        q = self.filter_by_date(query=q, model=ProductionPlanModel, year=year, months=months)
        q = self.filter_by_dict_names(query=q, dict_model=ShippingBasisDictModel, dict_names=basis_names)
        q = q.group_by(ShippingBasisDictModel.id, ShippingBasisDictModel.name, ProductionPlanModel.month)

        from sqlalchemy.dialects import postgresql
        # print(q.selectable.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))

        production_subq = (
            q.subquery()
        )
        
        # Максимум ресурса по каждому собственнику в рамках (basis_id, month)
        owner_resource_q = self.session.query(
            ShipmentsModel.shipping_basis_id.label('basis_id'),
            ShipmentsModel.month.label('month'),
            ShipmentsModel.product_owner_id.label('product_owner_id'),
            func.max(ShipmentsModel.all_resource).label('owner_max_resource'),
        ).select_from(ShipmentsModel)

        owner_resource_q = self.filter_by_dict_names(
            query=owner_resource_q,
            dict_model=ProductDictModel,
            dict_names=product_names,
        )
        if category_names:
            owner_resource_q = self.filter_by_dict_names(
                query=owner_resource_q,
                dict_model=ProductCategoryDictModel,
                dict_names=category_names,
            )
        owner_resource_q = self.filter_by_date(
            query=owner_resource_q,
            model=ShipmentsModel,
            year=year,
            months=months,
        )
        owner_resource_q = self.filter_by_dict_names(
            query=owner_resource_q,
            dict_model=ShippingBasisDictModel,
            dict_names=basis_names,
        )

        owner_resource_q = owner_resource_q.group_by(
            ShipmentsModel.shipping_basis_id,
            ShipmentsModel.month,
            ShipmentsModel.product_owner_id,
        )

        owner_resource_subq = owner_resource_q.subquery('owner_resource')

        # Сумма максимумов по собственникам
        owner_resource_sum_q = self.session.query(
            owner_resource_subq.c.basis_id,
            owner_resource_subq.c.month,
            func.sum(owner_resource_subq.c.owner_max_resource)
                .label('resource_for_distribution_by_owners'),
        ).group_by(
            owner_resource_subq.c.basis_id,
            owner_resource_subq.c.month,
        )

        owner_resource_sum_subq = owner_resource_sum_q.subquery('resource_for_distribution_by_owners')

        q = self.session.query(
                ShipmentsModel.shipping_basis_id.label('basis_id'),
                ShippingBasisDictModel.name.label('factory_name'),
                func.max(ShipmentsModel.all_resource).label('resource_for_distribution'),   # Ресурс к распределению
                func.sum(ShipmentsModel.accepted_deal).label('distributed_all'),             # Распределено, весь объём
                func.sum(
                        case((INNER_TRANS_DIR_CASE(ShipmentsModel), 
                                ShipmentsModel.accepted_deal), 
                                else_=None)
                        ).label('total_allocated'),                  # Всего выделено БК (Внутренний рынок)
                func.sum(
                        case(((INNER_TRANS_DIR_CASE(ShipmentsModel) & (STOCK_EXCESS_DEAL_CAT_CASE(ShipmentsModel) | STOCK_STATE_NECESSARY_DEAL_CAT_CASE(ShipmentsModel))), 
                              ShipmentsModel.accepted_deal
                              ),else_=None
                             )).label('stock_inner'),                # (Внутренний рынок) Всего биржа
                func.sum(
                        case(((INNER_TRANS_DIR_CASE(ShipmentsModel) & STOCK_STATE_NECESSARY_DEAL_CAT_CASE(ShipmentsModel)), 
                                ShipmentsModel.accepted_deal
                             ), else_=None
                        )).label('stock_necessary_inner'),           # (Внутренний рынок) Биржа. Обязательства.
                func.sum(
                        case(((INNER_TRANS_DIR_CASE(ShipmentsModel) & STOCK_EXCESS_DEAL_CAT_CASE(ShipmentsModel)), 
                                ShipmentsModel.accepted_deal
                             ), else_=None)
                        ).label('stock_add_inner'),                 # (Внутренний рынок) Биржа. Доп объёмы
                func.sum(
                        case(((INNER_TRANS_DIR_CASE(ShipmentsModel) & GOZ_DEAL_CAT_CASE(ShipmentsModel)), 
                                ShipmentsModel.accepted_deal), 
                            ),    else_=None
                    ).label('goz_inner'),                           # ГОЗ (Внутр. Рынок)
                func.sum(
                    case(((INNER_TRANS_DIR_CASE(ShipmentsModel) & WHOLESALE_DEAL_CAT_CASE(ShipmentsModel)), 
                            ShipmentsModel.accepted_deal), 
                            else_=None
                        )
                ).label('wholesale_inner'),                     # Мелкий Опт (Внутр. Рынок)
                func.sum(
                    case((and_(INNER_TRANS_DIR_CASE(ShipmentsModel), RETAIL_OPT_DEAL_CAT_CASE(ShipmentsModel)), 
                            ShipmentsModel.accepted_deal), 
                            else_=None
                        )
                ).label('retail_inner'),                        # Розница (Снабжение розничной сети) (Внутр. Рынок)
                func.sum(
                    case(((INNER_TRANS_DIR_CASE(ShipmentsModel) & LONG_TERM_DEAL_CAT_CASE(ShipmentsModel)), 
                            ShipmentsModel.accepted_deal), 
                            else_=None)
                ).label('binding_inner'),                       # “Обязательные” контракты (Внутр. Рынок)
                func.sum(
                    case(((INNER_TRANS_DIR_CASE(ShipmentsModel) & (OTHER_DEAL_CAT_CASE(ShipmentsModel) | FRAME_AGREEMENT_DEAL_CAT_CASE(ShipmentsModel))), 
                            ShipmentsModel.accepted_deal), 
                            else_=None)
                ).label('free_inner'),                          # Прочее (Внутр. Рынок)
                func.sum(
                    case((INNER_TRANS_DIR_CASE(ShipmentsModel), 
                            ShipmentsModel.value - ShipmentsModel.accepted_deal), 
                            else_=None)
                ).label('additional_need_inner'),               # Доп. потребность (Внутр. Рынок)
                func.sum(
                    case((EXPORT_TRANS_DIR_CASE(ShipmentsModel), 
                            ShipmentsModel.accepted_deal), 
                            else_=None)
                    ).label('export_total_allocated'),           # Всего выделено БК	(Экспорт)
                func.sum(
                    case(((EXPORT_TRANS_DIR_CASE(ShipmentsModel) & LONG_TERM_DEAL_CAT_CASE(ShipmentsModel)), 
                            ShipmentsModel.accepted_deal), 
                            else_=None)
                ).label('secure_inner'),                        # “Обязательные” контракты (Экспорт)
                func.sum(
                    case(((EXPORT_TRANS_DIR_CASE(ShipmentsModel) & (OTHER_DEAL_CAT_CASE(ShipmentsModel) | FRAME_AGREEMENT_DEAL_CAT_CASE(ShipmentsModel))), 
                            ShipmentsModel.accepted_deal), 
                            else_=None)
                ).label('free_export'),                          # Прочее (Экспорт)
                func.sum(
                    case((EXPORT_TRANS_DIR_CASE(ShipmentsModel), 
                            ShipmentsModel.value - ShipmentsModel.accepted_deal), 
                            else_=None)
                ).label('additional_need_export'),              # Доп. потребность (Экспорт)
                func.sum(
                    case((NEEDS_TRANS_DIR_CASE(ShipmentsModel), 
                            ShipmentsModel.accepted_deal), 
                            else_=None)
                ).label('needs_total_allocated'),               # Всего выделено БК (Нужды ДО)
                func.sum(
                    case((NEEDS_TRANS_DIR_CASE(ShipmentsModel), 
                            ShipmentsModel.value - ShipmentsModel.accepted_deal), 
                            else_=None)
                ).label('additional_need_needs'),               # Доп. потребность (Нужды ДО)
                (func.max(ShipmentsModel.all_resource) - func.sum(ShipmentsModel.accepted_deal)).label('resource_left_after_appl'),         # Остаток ресурса после заявки,
                ShipmentsModel.month
                ).select_from(ShipmentsModel)
                
        q = self.filter_by_dict_names(query=q, dict_model=ProductDictModel, dict_names=product_names)
        if category_names:
            q = self.filter_by_dict_names(query=q, dict_model=ProductCategoryDictModel, dict_names=category_names)
        q = self.filter_by_date(query=q, model=ShipmentsModel, year=year, months=months)
        q = self.filter_by_dict_names(query=q, dict_model=ShippingBasisDictModel, dict_names=basis_names)
        q = q.group_by(ShipmentsModel.shipping_basis_id, ShippingBasisDictModel.name, ShipmentsModel.month)
        
        shipments_subq = (
            q.subquery()
        )

        query = (
            self.session.query(
                shipments_subq.c.factory_name.label('basis_name'),
                production_subq.c.leftovers,
                production_subq.c.production_plan,
                func.coalesce(
                    owner_resource_sum_subq.c.resource_for_distribution_by_owners,
                    shipments_subq.c.resource_for_distribution,
                ).label('resource_for_distribution'),
                shipments_subq.c.distributed_all,
                shipments_subq.c.total_allocated,
                shipments_subq.c.stock_inner,
                shipments_subq.c.stock_necessary_inner,
                shipments_subq.c.stock_add_inner,
                shipments_subq.c.goz_inner,
                shipments_subq.c.wholesale_inner,
                shipments_subq.c.retail_inner,
                shipments_subq.c.binding_inner,
                shipments_subq.c.free_inner,
                shipments_subq.c.additional_need_inner,
                shipments_subq.c.export_total_allocated,
                shipments_subq.c.secure_inner,
                shipments_subq.c.free_export,
                shipments_subq.c.additional_need_export,
                shipments_subq.c.needs_total_allocated,
                shipments_subq.c.additional_need_needs,
                (
                    func.coalesce(
                        owner_resource_sum_subq.c.resource_for_distribution_by_owners,
                        shipments_subq.c.resource_for_distribution,
                    )
                    - func.coalesce(shipments_subq.c.distributed_all, 0)
                ).label('resource_left_after_appl'),
                shipments_subq.c.month,
            )
            .select_from(production_subq)
            .outerjoin(
                shipments_subq,
                and_(
                    production_subq.c.basis_id == shipments_subq.c.basis_id,
                    production_subq.c.month == shipments_subq.c.month,
                ),
            )
            .outerjoin(
                owner_resource_sum_subq,
                and_(
                    production_subq.c.basis_id == owner_resource_sum_subq.c.basis_id,
                    production_subq.c.month == owner_resource_sum_subq.c.month,
                ),
            )
        )

        return query.all()


    def get_factory_income(self, 
                           product_names: Union[str, List[str]],
                           category_names: Union[str, List[str]], 
                           year: int, 
                           months: Union[int, List[int]],
                           basis_names=None, 
                           *args, **kwargs) -> Optional[List[ShipmentsModel]]: # заводы
        query = self.session.query(
            ShippingBasisDictModel,
            TransDirDictModel,
            ShipmentsModel,
            UnitDictModel
        ).with_entities(ShippingBasisDictModel.name.label('shipping_basis'),
            TransDirDictModel.name.label('trans_dir'),
            func.sum(ShipmentsModel.cost_x_value).label('total_cost'),
            func.sum(ShipmentsModel.cost).label('cost'),
            func.sum(ShipmentsModel.value).label('total_value'),
            UnitDictModel.name.label('unit')).filter(*args).filter_by(**kwargs)

        query = query.join(TransDirDictModel).join(UnitDictModel)

        query = self.filter_by_dict_names(query=query, dict_model=ProductDictModel, dict_names=product_names)
        query = self.filter_by_date(query=query, model=ShipmentsModel, year=year, months=months)
        query = self.filter_by_dict_names(query=query, dict_model=ShippingBasisDictModel, dict_names=basis_names)
        if category_names:
            query = self.filter_by_dict_names(query=query, dict_model=ProductCategoryDictModel, dict_names=category_names)

        query = query.group_by(
            ShippingBasisDictModel.name, TransDirDictModel.name, UnitDictModel.name
        )

        query = query.order_by(ShippingBasisDictModel.name, TransDirDictModel.name)
        
        return query.all()

    def get_waterfall_data(
        self,
        product_names: Union[str, List[str]],
        category_names: Union[str, List[str]],
        year: int,
        months: Union[int, List[int]],
        basis_names=None,
        *args, **kwargs
    ) -> Optional[List[ShipmentsModel]]:
        # сумма принятых заявок (по заводам и месяцам)
        sum_accept_zayav_q = self.session.query(
            func.sum(ShipmentsModel.accepted_deal).label('sum_accepted_deal'),
            ShipmentsModel.shipping_basis_id.label('shipping_basis_id'),
            ShipmentsModel.month.label('month'),
        ).select_from(ShipmentsModel)

        sum_accept_zayav_q = self.filter_by_dict_names(
            query=sum_accept_zayav_q,
            dict_model=ProductDictModel,
            dict_names=product_names,
        )
        sum_accept_zayav_q = self.filter_by_date(
            query=sum_accept_zayav_q,
            model=ShipmentsModel,
            year=year,
            months=months,
        )
        sum_accept_zayav_q = self.filter_by_dict_names(
            query=sum_accept_zayav_q,
            dict_model=ShippingBasisDictModel,
            dict_names=basis_names,
        )
        sum_accept_zayav_q = self.filter_by_dict_names(
            query=sum_accept_zayav_q,
            dict_model=ProductCategoryDictModel,
            dict_names=category_names,
        )

        sum_accept_zayav_q = sum_accept_zayav_q.group_by(
            ShipmentsModel.shipping_basis_id,
            ShipmentsModel.month,
        )
        sum_accept_zayav_subq = sum_accept_zayav_q.subquery()

        # максимум ресурса по КАЖДОМУ собственнику в рамках (basis, month)
        owner_resource_q = self.session.query(
            ShipmentsModel.shipping_basis_id.label('shipping_basis_id'),
            ShipmentsModel.month.label('month'),
            ShipmentsModel.product_owner_id.label('product_owner_id'),
            func.max(ShipmentsModel.all_resource).label('owner_max_resource'),
        ).select_from(ShipmentsModel)

        owner_resource_q = self.filter_by_dict_names(
            query=owner_resource_q,
            dict_model=ProductDictModel,
            dict_names=product_names,
        )
        owner_resource_q = self.filter_by_date(
            query=owner_resource_q,
            model=ShipmentsModel,
            year=year,
            months=months,
        )
        owner_resource_q = self.filter_by_dict_names(
            query=owner_resource_q,
            dict_model=ShippingBasisDictModel,
            dict_names=basis_names,
        )
        owner_resource_q = self.filter_by_dict_names(
            query=owner_resource_q,
            dict_model=ProductCategoryDictModel,
            dict_names=category_names,
        )

        owner_resource_q = owner_resource_q.group_by(
            ShipmentsModel.shipping_basis_id,
            ShipmentsModel.month,
            ShipmentsModel.product_owner_id,
        )
        owner_resource_subq = owner_resource_q.subquery('owner_resource')

        # Сумма максимумов по собственникам → тот самый ресурс к распределению по (basis, month)
        owner_resource_sum_q = self.session.query(
            owner_resource_subq.c.shipping_basis_id.label('shipping_basis_id'),
            owner_resource_subq.c.month.label('month'),
            func.sum(owner_resource_subq.c.owner_max_resource).label('max_all_res'),
        ).group_by(
            owner_resource_subq.c.shipping_basis_id,
            owner_resource_subq.c.month,
        )
        owner_resource_sum_subq = owner_resource_sum_q.subquery('owner_resource_sum')

        # остаток ресурса = (ресурс по собственникам) - (принятые заявки)
        leftovers_q = self.session.query(
            owner_resource_sum_subq.c.month.label('month'),
            owner_resource_sum_subq.c.shipping_basis_id.label('shipping_basis_id'),
            owner_resource_sum_subq.c.max_all_res.label('max_all_res'),
            (owner_resource_sum_subq.c.max_all_res - sum_accept_zayav_subq.c.sum_accepted_deal)
                .label('leftovers'),
        ).select_from(owner_resource_sum_subq).outerjoin(
            sum_accept_zayav_subq,
            and_(
                owner_resource_sum_subq.c.shipping_basis_id == sum_accept_zayav_subq.c.shipping_basis_id,
                owner_resource_sum_subq.c.month == sum_accept_zayav_subq.c.month,
            ),
        )
        leftovers_subq = leftovers_q.subquery('leftovers')

        query = (
            self.session.query(
                ShippingBasisDictModel.name.label('shipping_basis'),
                func.max(ShipmentsModel.plan).label('total_plan'),
                func.max(ShipmentsModel.leftovers).label('total_leftovers'),
                func.max(ShipmentsModel.restrictions).label('available_restriction'),
                # Доступный ресурс считаем как сумму ресурса по собственникам
                func.max(leftovers_subq.c.max_all_res).label('available_available'),
                func.sum(
                    case(
                        (INNER_TRANS_DIR_CASE(ShipmentsModel), ShipmentsModel.accepted_deal),
                        else_=None,
                    )
                ).label('inner_value'),
                func.sum(
                    case(
                        (EXPORT_TRANS_DIR_CASE(ShipmentsModel), ShipmentsModel.accepted_deal),
                        else_=None,
                    )
                ).label('export_value'),
                func.sum(
                    case(
                        (NEEDS_TRANS_DIR_CASE(ShipmentsModel), ShipmentsModel.accepted_deal),
                        else_=None,
                    )
                ).label('needs_value'),
                func.sum(
                    ShipmentsModel.value - ShipmentsModel.accepted_deal
                ).label('add_need'),
                func.sum(
                    case(
                        (INNER_TRANS_DIR_CASE(ShipmentsModel), ShipmentsModel.value - ShipmentsModel.accepted_deal),
                        else_=None,
                    )
                ).label('inner_claim'),
                func.sum(
                    case(
                        (EXPORT_TRANS_DIR_CASE(ShipmentsModel), ShipmentsModel.value - ShipmentsModel.accepted_deal),
                        else_=None,
                    )
                ).label('export_claim'),
                func.sum(
                    case(
                        (NEEDS_TRANS_DIR_CASE(ShipmentsModel), ShipmentsModel.value - ShipmentsModel.accepted_deal),
                        else_=None,
                    )
                ).label('needs_claim'),
                leftovers_subq.c.leftovers.label('leftovers'),
            )
            .select_from(ShipmentsModel)
            .join(
                leftovers_subq,
                and_(
                    ShipmentsModel.shipping_basis_id == leftovers_subq.c.shipping_basis_id,
                    ShipmentsModel.month == leftovers_subq.c.month,
                ),
            )
        )

        query = self.filter_by_dict_names(
            query=query,
            dict_model=ProductDictModel,
            dict_names=product_names,
            join_condition=(ShipmentsModel.product_id == ProductDictModel.id),
        )
        query = self.filter_by_date(
            query=query,
            model=ShipmentsModel,
            year=year,
            months=months,
        )
        query = self.filter_by_dict_names(
            query=query,
            dict_model=ShippingBasisDictModel,
            dict_names=basis_names,
            join_condition=(ShipmentsModel.shipping_basis_id == ShippingBasisDictModel.id),
        )
        query = self.filter_by_dict_names(
            query=query,
            dict_model=ProductCategoryDictModel,
            dict_names=category_names,
            join_condition=(ProductDictModel.product_category_id == ProductCategoryDictModel.id),
        )

        query = query.group_by(
            ShippingBasisDictModel.name,
            leftovers_subq.c.leftovers,
        )

        return query.all()
    
    def add(self, model, *args, **kwargs):
        raise NotImplementedError()
    
    def get_all(self, model, *args, **kwargs):
        raise NotImplementedError()
    
    def get_by_id(self, id: int, *args, **kwargs):
        raise NotImplementedError()
