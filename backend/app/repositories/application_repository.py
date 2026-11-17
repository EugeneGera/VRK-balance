from app.repositories.mixins import DateFilterMixin, DictsFilterMixin, ShipmentsFilterMixin
from sqlalchemy.orm import scoped_session
from typing import List
from app.repositories.repository import BaseRepository
from app.entities.models import ProductCategoryDictModel, TransApplicationModel, ProductDictModel, ShippingBasisDictModel
from app.core.errors import NotFoundError


class ApplicationRepository(BaseRepository, DateFilterMixin, ShipmentsFilterMixin, DictsFilterMixin):   
    def __init__(self, session: scoped_session):
        self.session = session
    
    def get_all(self,                            # Получить все модели справочника
                **filters
               ) -> List[str]:

        query = self.session.query(TransApplicationModel).select_from(TransApplicationModel)
        query = self.filter_by_date(query, model=TransApplicationModel, year=filters['year'], months=filters['months'])#(filters['month_start'], filters['month_end']))

        # Скрываем нули
        if 'hide_zero' in filters and filters['hide_zero'] == True:
            query = query.filter(TransApplicationModel.value != 0 or TransApplicationModel.cost != 0)

        query = self.filter_by_dict_names(query=query, dict_model=ProductDictModel, dict_names=filters['product'])
        query = self.filter_by_dict_names(query=query, dict_model=ProductCategoryDictModel, dict_names=filters['category_product'], join_condition=ProductDictModel.product_category_id==ProductCategoryDictModel.id)

        query = self.filter_by_dict_names(query=query, dict_model=ShippingBasisDictModel, dict_names=filters['basises']) 


        # Возвращаем список результатов
        query = query.order_by(TransApplicationModel.year, TransApplicationModel.month, TransApplicationModel.id)

        return query.all()
    
    def get_by_id(self, id : int,                # Получить модель по id
                *args, **kwargs
               ) -> List[str]:
        return self.session.query(TransApplicationModel).filter(TransApplicationModel.id == id).filter(*args).filter_by(**kwargs).first()
    
    def add(self, model):
        raise NotImplementedError()
    
    def update(self, fields_to_update):
        try:     
            for application in fields_to_update:
                existing_data = self.get_by_id(id=application["id"])

                if not existing_data:
                    raise NotFoundError(model="ApplicationModel", key=f"id={id}")

                for field_name, new_value in application.items():
                     setattr(existing_data, field_name, new_value)
                
                #existing_data = calc_resource(existing_data)

                #plan["resource"] = existing_data.resource
       
            self.session.bulk_update_mappings(TransApplicationModel, fields_to_update)
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
    #         raise NotFoundError(model="TransApplicationModel", key=f"id={id}")
        
    #     # Обновление полей
    #     for field_name, new_value in fields_to_update.items():
    #         setattr(existing_data, field_name, new_value)

    #     # Попытка сохранения изменений
    #     try:
    #         self.session.commit()
    #     except Exception as err:
    #         self.session.rollback()
    #         raise
    #     finally:
    #         self.session.close()
        
    #     return fields_to_update