import re
from typing import Any, Dict, List, Optional, Union
from flask import session
from sqlalchemy import text
from sqlalchemy.orm import scoped_session

from app.repositories.dict_repositories import ProductDictRepository, UnitDictRepository, ProductCategoryDictRepository
from app.repositories.shipments_repository import ShipmentsRepository
from app.entities.db_connection import set_db_connection

class FilterSessionService:
    @staticmethod
    def set_filters(filter_name: str, filters: Dict[str, Any]) -> None:
        if not session.get('bk_filters'):
                session['bk_filters'] = {}
        session['bk_filters'][filter_name] = {
                'data': filters,
            }
        session.modified = True

    @staticmethod
    def get_filters(filter_name: str) -> Optional[Dict[str, Any]]:
        return session.get('bk_filters', {}).get(filter_name, {}).get('data')

    @staticmethod
    def clear_filters(filter_name: str) -> None:
        if 'bk_filters' in session and filter_name in session['bk_filters']:
            session['bk_filters'].pop(filter_name)
            session.modified = True
        
    @staticmethod
    def clear_all_filters() -> None:
        if 'bk_filters' in session:
            session.pop('bk_filters')
            session.modified = True

    @staticmethod
    def update_product_filter(session, year: int,       ##### это какой-то треш
                              months: List[int],
                              basis_names: List[str],
                              product_names: Optional[Union[List[str], str]] = None,
                              category_names: Optional[Union[List[str], str]] = None):
            prev_filters = {
                'unit_names': FilterSessionService.get_filters('unit_names'),
                'product_names': FilterSessionService.get_filters('product_names'),
                'category_names': FilterSessionService.get_filters('category_names'),
                }
            
            if prev_filters['category_names'] == category_names:
                return prev_filters # если этот фильтр уже поставлен
            
            if category_names is None:

                # если нет категорий - то берём первую "Рабочую"
                shipped_categories = ShipmentsRepository(session).get_shipped_categories(year=year, 
                                                                                months=months, 
                                                                                basis_names=basis_names)
                if shipped_categories is None:
                    pass # TODO! если нет доступных категорий???
                else:
                    category = shipped_categories[0]
                    category_names = category.name
                    category_ids = category.id
                # продукты оставляем налл
                product_names = None
                product_ids = None
                
            else:
                 # категория есть - устанавливаем фильтры
                category_ids = ProductCategoryDictRepository(session).get_by_names(category_names)[0].id

                # если есть продукты в квери - ставим, если нет - оставляем налл
                product_ids = None
                if product_names is not None and prev_filters['product_names'] != product_names: # проверка, что фильтр по продуктам ещё не поставлен
                    product_ids = [product.id for product in ProductDictRepository(session).get_by_names(product_names)]
    
            # если есть product_names - unit_names берём для первого, иначе ставим null
            unit_names = None
            shipped_product_ids = None
            if product_ids is None:
                shipped_product_ids = ShipmentsRepository(session).get_shipped_product(year=year, 
                                                                months=months,
                                                                category_names=category_names, 
                                                                basis_names=basis_names)

            if shipped_product_ids is not None and len(shipped_product_ids) > 0:
                    unit = ProductDictRepository(session).get_by_id(shipped_product_ids[0]).unit
                    unit_names = None if unit is None else unit.name
            if product_ids is not None and len(product_ids) > 0:
                unit = ProductDictRepository(session).get_by_id(product_ids[0]).unit
                unit_names = None if unit is None else unit.name

            # если в итоге unit_names так и не были определены, берём первые из тех, которые относятся к категории продукта
            if unit_names is None and category_ids is not None:
                 category = ProductCategoryDictRepository(session).get_first_unit_by_id(category_ids)
            # 'морозим' фильтры
            filters = {
                'product_ids': product_ids,
                'product_names': product_names,
                'unit_names' : unit_names,
                'category_names': category_names,
                'category_ids': category_ids
            }
            FilterSessionService.set_filters('product_filters', filters)
            # возвращаем значения
            return FilterSessionService.get_filters('product_filters')

def execute_sql_file(sql_file_path: str, session: scoped_session, **kwargs):
    with open(sql_file_path, 'r', encoding='utf-8-sig') as file:
        sql_script = file.read()
    
    # Удаление комментов
    sql_script = re.sub(r'--.*?\n', '', sql_script)  
    sql_script = re.sub(r'\/\/.*?\n', '', sql_script) 
    sql_script = re.sub(r'/\*.*?\*/', '', sql_script, flags=re.DOTALL) 
    
    # Отдельные стейтменты
    statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
    
    connection = session.connection()
    
    try:
        for stmt in statements:
            if stmt[-1] != ';':
                 stmt += ';'
            if stmt:  # минус пустые строки
                connection.execute(text(stmt), kwargs)
        session.commit()  
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
