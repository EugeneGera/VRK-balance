from sqlalchemy import Boolean, ColumnElement, and_
from typing import Any, Optional, List, Type, Union

from app.entities.models import ShipmentsModel

def add_date_filters(query, model, year: Optional[int] = None, 
                     months: Optional[List[int]] = None,
                     ):
    filters = []
    
    if year is not None:
        filters.append(model.year == year)
    
    if months:
        filters.append(model.month.in_(ensure_list(months)))
    
    if filters:
        query = query.filter(and_(*filters))
    
    return query

def ensure_list(obj: Any):
    if isinstance(obj, list):
        return obj
    if obj is not None:
        return [obj]

def calc_resource(calc_data: Any):
    if calc_data.left is None:
        calc_data.left = 0
    
    if calc_data.plan is None:
        calc_data.plan = 0
    
    if calc_data.min_left is None:
        calc_data.min_left = 0
    
    if calc_data.max_shipment is None:
        calc_data.max_shipment = 0

    min = calc_data.left + calc_data.plan - calc_data.min_left
    if ( min < calc_data.max_shipment and min != 0 ) or ( calc_data.max_shipment == 0 ):
        calc_data.resource = min
    else:
        calc_data.resource = calc_data.max_shipment
    
    return calc_data
    

def add_filter_by_dict_names(query, dict_model, model_names: Union[str, List[str]]=None, join_condition: Optional[Boolean] = None):
    query = query.filter(dict_model.name.in_(ensure_list(model_names))).join(dict_model, onclause=join_condition)
    return query


def add_filter_by_dict_ids(query, model, dict_model, model_names: Union[str, List[str]]=None):
    raise NotImplementedError()


def add_filter_by_basis_ids(query, model, basis_ids: Union[int, List[int]] = None):
    query = query.filter(model.shipping_basis_id.in_(ensure_list(basis_ids)))
    return query

def add_filter_by_product_ids(query, model, product_ids: Union[int, List[int]] = None):
    query = query.filter(model.product_id.in_(ensure_list(product_ids)))
    return query


################### CASES
################### ключи фильтрации
########### Направление реализации
INNER_TRANS_DIR_CASE: ColumnElement[bool] = lambda model: (model.trans_dir_id == 2) # Направление реализации - внутренний рынок
EXPORT_TRANS_DIR_CASE: ColumnElement[bool] = lambda model: (model.trans_dir_id == 3) # Направление реализации - экспорт
NEEDS_TRANS_DIR_CASE: ColumnElement[bool] = lambda model: (model.trans_dir_id == 1) # Направление реализации - нужды ДО

########### Канал сбыта
SECURE_DISTR_CHANNEL_CASE: ColumnElement[bool] = lambda model: (model.distr_channel_id == 1) # канал сбыта - защищено
FREE_DISTR_CHANNEL_CASE: ColumnElement[bool] = lambda model: (model.distr_channel_id == 2) # канал сбыта - свободно

########### Типы сделки
STATE_NECESSARY_DEAL_TYPE_CASE: ColumnElement[bool] = lambda model: (model.deal_type_id == 1) # Тип сделки - Гос. Обязательства
WHOLESALE_DEAL_TYPE_CASE: ColumnElement[bool] = lambda model: (model.deal_type_id == 2) # Тип сделки - Мелкий опт
RETAIL_OPT_DEAL_TYPE_CASE: ColumnElement[bool] = lambda model: (model.deal_type_id == 3) # Тип сделки - Розница
LENGTHY_CONTRACT_DEAL_TYPE_CASE: ColumnElement[bool] = lambda model: (model.deal_type_id == 4) # Тип сделки - Долгосрочные контракты
OTHER_DEAL_TYPE_CASE: ColumnElement[bool] = lambda model: (model.deal_type_id == 5) # Тип сделки - Прочие
NEEDS_DEAL_TYPE_CASE: ColumnElement[bool] = lambda model: (model.deal_type_id == 6) # Тип сделки - Нужды ДО


########### Категории сделки
NEEDS_DEAL_CAT_CASE: ColumnElement[bool] = lambda model: (model.deal_category_id == 1) # Нужды ДО
LONG_TERM_DEAL_CAT_CASE: ColumnElement[bool] = lambda model: (model.deal_category_id == 6)# Долгосрочные контракты
RETAIL_OPT_DEAL_CAT_CASE: ColumnElement[bool] = lambda model: (model.deal_category_id == 4) # Снабжение розничной сети
WHOLESALE_DEAL_CAT_CASE: ColumnElement[bool] = lambda model: (model.deal_category_id == 5) # Мелкий опт
GOZ_DEAL_CAT_CASE: ColumnElement[bool] = lambda model: (model.deal_category_id == 2) # ГОЗ
STOCK_STATE_NECESSARY_DEAL_CAT_CASE: ColumnElement[bool] = lambda model: (model.deal_category_id == 3) # Гос. Обязательства. Биржа
FRAME_AGREEMENT_DEAL_CAT_CASE: ColumnElement[bool] = lambda model: (model.deal_category_id == 7) # Рамочный договор
STOCK_EXCESS_DEAL_CAT_CASE: ColumnElement[bool] = lambda model: (model.deal_category_id == 8) # Биржа (сверх обязательства)
OTHER_DEAL_CAT_CASE: ColumnElement[bool] = lambda model: (model.deal_category_id == 9) # Прочие контракты