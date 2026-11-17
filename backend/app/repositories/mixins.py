from typing import Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy import Boolean
from app.repositories.utils import add_date_filters, add_filter_by_basis_ids, add_filter_by_dict_names, add_filter_by_product_ids
from app.entities.models import AgentDictModel, ClientDictModel, DealCategoryDictModel, DealStatusDictModel, DealTypeDictModel, DestinationDictModel, DistrChannelDictModel, OrgDictModel, ProductCategoryDictModel, ProductDictModel, ProductOwnerDictModel, RecordOwnerDictModel, ShippingBasisDictModel, TransDirDictModel, TransportDictModel, UnitDictModel
from sqlalchemy.orm import Query

# Model = TypeVar('Model',                       # Все модели
#                     ShippingBasisDictModel, 
#                     ProductDictModel, 
#                     ProductCategoryDictModel, 
#                     DealCategoryDictModel, 
#                     UnitDictModel, 
#                     DistrChannelDictModel, 
#                     TransDirDictModel, 
#                     OrgDictModel, 
#                     RecordOwnerDictModel, 
#                     AgentDictModel, 
#                     ProductOwnerDictModel, 
#                     DealStatusDictModel, 
#                     TransportDictModel, 
#                     DealTypeDictModel, 
#                     DestinationDictModel, 
#                     ClientDictModel,
#                     ShipmentsModel) 

class DateFilterMixin:
    @staticmethod
    def filter_by_date(query: Query, model: Type, year=None, months: Union[int, List[int]]=None):

        return add_date_filters(query, model, year, months)
    
class ShipmentsFilterMixin:
    # @staticmethod
    # def filter_by_basis_ids(query: Query, model: Type, basis_ids: Union[int, List[int]]=None):
    #     if basis_ids is not None:
    #         query = add_filter_by_basis_ids(query, model, basis_ids)
    #     return query
    
    @staticmethod
    def filter_by_product_ids(query: Query, model: Type, product_ids: Union[int, List[int]]=None):
        if product_ids is not None:
            query = add_filter_by_product_ids(query, model, product_ids)
        return query
    
class DictsFilterMixin:
    @staticmethod
    def filter_by_dict_names(query: Query, dict_model: Type, dict_names: Union[str, List[str]]=None, join_condition: Optional[Boolean] = None):

        if dict_names is not None and len(dict_names) > 0:
            query = add_filter_by_dict_names(query, dict_model=dict_model, model_names=dict_names, join_condition=join_condition)
        else:
            query = query.join(dict_model, onclause=join_condition)
        return query
    
    @staticmethod
    def filter_by_dict_ids(query: Query, dict_model: Type, dict_ids: Union[int, List[int]]=None):
        raise NotImplementedError()

    
