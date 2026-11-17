from app.repositories.mixins import DateFilterMixin, DictsFilterMixin, ShipmentsFilterMixin
from sqlalchemy.orm import scoped_session
from typing import List
from app.repositories.repository import BaseRepository
from app.repositories.utils import calc_resource
from app.entities.models import ProductCategoryDictModel, ProductionPlanModel, ProductDictModel, ShippingBasisDictModel
from app.core.errors import NotFoundError


class PlanRepository(DateFilterMixin, ShipmentsFilterMixin, DictsFilterMixin):   
    def __init__(self, session: scoped_session):
        self.session = session
    
    def get_all(self,                            # Получить все модели справочника
                name_jurnal,
                **filters
               ) -> List[str]:
        
        # Базовая выборка всех записей из таблицы TransApplicationModel
        query = self.session.query(ProductionPlanModel)

        query = self.filter_by_date(query, model=ProductionPlanModel, year=filters['year'], months=filters['months'])#(filters['month_start'], filters['month_end']))

        # Скрываем нули
        if 'hide_zero' in filters and filters['hide_zero'] == True:
            if name_jurnal == 'plan':
                query = query.filter(ProductionPlanModel.plan != 0)
            elif name_jurnal == 'leftover':
                query = query.filter(ProductionPlanModel.left != 0)
            elif name_jurnal == 'limit':
                query = query.filter(ProductionPlanModel.min_left != 0 or ProductionPlanModel.max_shipment) 
        query = self.filter_by_dict_names(query=query, dict_model=ProductDictModel, dict_names=filters['product'])
        query = self.filter_by_dict_names(query=query, dict_model=ProductCategoryDictModel, dict_names=filters['category_product'], join_condition=ProductDictModel.product_category_id==ProductCategoryDictModel.id)
        query = self.filter_by_dict_names(query=query, dict_model=ShippingBasisDictModel, dict_names=filters['basises']) 

        # # Фильтр по продуктам
        # if 'product' in filters:
        #     query = query.join(ProductDictModel).filter(
        #         ProductDictModel.name.in_(filters['product'])
        #     )
        
        # Фильтр по заводу
        # if 'basises' in filters:
        #     query = query.join(ShippingBasisDictModel).filter(
        #         ShippingBasisDictModel.name.in_(filters['basises'])
        #     )

        # Возвращаем список результатов
        query = query.order_by(ProductionPlanModel.year, ProductionPlanModel.month, ProductionPlanModel.id)

        return query.all()
    
    def get_by_id(self, id : int,                # Получить модель по id
                *args, **kwargs
               ) -> List[str]:
        return self.session.query(ProductionPlanModel).filter(ProductionPlanModel.id == id).filter(*args).filter_by(**kwargs).first()
    
    def add(self, model):
        raise NotImplementedError()
    
    def update(self, fields_to_update):
        try:     
            for plan in fields_to_update:
                existing_data = self.get_by_id(id=plan["id"])

                if not existing_data:
                    raise NotFoundError(model="ProductionPlanModel", key=f"id={id}")

                for field_name, new_value in plan.items():
                     setattr(existing_data, field_name, new_value)
                
                existing_data = calc_resource(existing_data)

                plan["resource"] = existing_data.resource
       
            self.session.bulk_update_mappings(ProductionPlanModel, fields_to_update)
            self.session.commit()
            return fields_to_update
        
        except Exception as e:
            self.session.rollback()
            raise
        
        # finally:
        #     self.session.close()
    
    # def update(self, **fields_to_update):
    #     # Получение ID из передаваемых аргументов
    #     if 'id' not in fields_to_update:
    #         raise ValueError("Field not specified 'id'")
        
    #     id = fields_to_update['id']

    #     # Поиск существующей записи
    #     existing_data = self.get_by_id(id=id)
    #     if not existing_data:
    #         raise NotFoundError(model="ProductionPlanModel", key=f"id={id}")

    #     # Обновление полей
    #     for field_name, new_value in fields_to_update.items():
    #         setattr(existing_data, field_name, new_value)
        
    #     # пересчитать ресурс
    #     existing_data = calc_resource(existing_data)
        
    #     # Попытка сохранения изменений
    #     try:
    #         self.session.commit()
    #     except Exception as err:
    #         self.session.rollback()
    #         raise
    #     finally:
    #         self.session.close()
        
    #     return fields_to_update