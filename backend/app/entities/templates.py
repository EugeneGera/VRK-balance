from typing import Optional
from sqlalchemy.orm import relationship
import sqlalchemy as sa
import sqlalchemy.orm as so


from app.entities.db_connection import Base


# TODO! убрать COLUMNS везде

class BaseTemplate():
    START_ROW = 1
    SHEET_NAME = ''
    COLUMNS = []

    @classmethod
    def get_display_to_column_map(cls):
        mapper = sa.inspect(cls)
        column_map = {}
        for column in mapper.attrs:
            column_info = column.columns[0].info
            if hasattr(column, 'info') and 'display' in column_info:
                column_map[column_info['display']] = column.key
        return column_map
    
    @classmethod
    def create_from_row(cls, row_data):
        display_map = cls.get_display_to_column_map()
        
        kwargs = {}

        for display_name, value in row_data.items():
            if display_name in display_map:
                column_name = display_map[display_name]
                # print(column_name, value)
                kwargs[column_name] = value if value != '' and value != '-' else None
        # print('кварги', kwargs)
        return cls(**kwargs)
    
    @classmethod
    def get_display_columns(cls):
        display_columns = []
        mapper = sa.inspect(cls)
        
        for column in mapper.attrs:
            if 'display' in column.columns[0].info:
                display_columns.append(column.info['display'])
        
        return display_columns
    
    def __repr__(self):
        return '{0} object (id {1})'.format(type(self), self.id)

class TransApplicationTemplate(Base, BaseTemplate):
    START_ROW = 4
    SHEET_NAME = 'Заявки'
    COLUMNS = [
                '№', 'Владелец записи', 'Месяц', 'Базис отгрузки', 'Продукт', 
                'Ед. изм.', 'Направление реализации', 'Агент / производитель', 
                'Собственник продукта', 'Способ отгрузки', 'Категория сделки', 
                'Станция (пункт) назначения', 'Покупатель', 'Статус заключения сделки', 
                'Объем по заявке, ед. изм.', 
                'Цена, руб./т (для газов руб./м3)', # !!! Надо обратить внимание в каких-то файлах столбец называется иначе
                'Примечание',
                'Категория продукта', 'Тип сделки', 'Канал сбыта'
            ]

    __tablename__ = 'tab_sh_zayav_real_bk'

    id = so.mapped_column(sa.Integer, primary_key=True, info={'display': '№'})
    tab_owner_bk_ids = so.mapped_column(sa.String, info={'display': 'Владелец записи'})
    month = so.mapped_column(sa.String, info={'display': 'Месяц'})
    tab_bazis_bk_ids = so.mapped_column(sa.String, info={'display': 'Базис отгрузки'})
    tab_product_bk_ids = so.mapped_column(sa.String, info={'display': 'Продукт'})
    tab_ei_bk_ids = so.mapped_column(sa.String, info={'display': 'Ед. изм.'})
    tab_napr_real_bk_ids = so.mapped_column(sa.String, info={'display': 'Направление реализации'})
    tab_proizv_bk_ids = so.mapped_column(sa.String, info={'display': 'Агент / производитель'})
    tab_sobstv_bk_ids = so.mapped_column(sa.String, info={'display': 'Собственник продукта'})
    tab_type_otgruz_bk_ids = so.mapped_column(sa.String, info={'display': 'Способ отгрузки'})
    tab_category_sd_bk_ids = so.mapped_column(sa.String, info={'display': 'Категория сделки'})
    tab_point_to_bk_ids = so.mapped_column(sa.String, info={'display': 'Станция (пункт) назначения'})
    tab_pokup_bk_ids = so.mapped_column(sa.String, info={'display': 'Покупатель'})
    tab_status_sd_bk_ids = so.mapped_column(sa.String, info={'display': 'Статус заключения сделки'})
    value = so.mapped_column(sa.String, info={'display': 'Объем по заявке, ед. изм.'})
    cost = so.mapped_column(sa.String, info={'display': 'Цена, руб./ед. изм.'}) # !!! Надо обратить внимание в каких-то файлах столбец называется иначе
    comment = so.mapped_column(sa.String, info={'display': 'Примечание'})
    tab_category_product_bk_ids = so.mapped_column(sa.String, info={'display': 'Категория продукта'})

class RestrictionsTemplate(Base, BaseTemplate): # Шаблон ограничения
    START_ROW = 5
    SHEET_NAME = 'Ограничения'
    COLUMNS = [
                '№', 'Ед. изм.', 'Базис отгрузки', 'Продукт', 'Собственник продукта', 'Агент / производитель',
                'Мин. остаток, месяц 1', 'Мин. остаток, месяц 2', 'Мин. остаток, месяц 3', 'Мин. остаток, месяц 4',
                'Мин. остаток, месяц 5', 'Мин. остаток, месяц 6', 'Мин. остаток, месяц 7', 'Мин. остаток, месяц 8',
                'Мин. остаток, месяц 9', 'Мин. остаток, месяц 10', 'Мин. остаток, месяц 11', 'Мин. остаток, месяц 12', 'Комментарий, при необходимости',
                'Макс. остаток, месяц 1', 'Макс. остаток, месяц 2', 'Макс. остаток, месяц 3', 'Макс. остаток, месяц 4',
                'Макс. остаток, месяц 5', 'Макс. остаток, месяц 6', 'Макс. остаток, месяц 7', 'Макс. остаток, месяц 8',
                'Макс. остаток, месяц 9', 'Макс. остаток, месяц 10', 'Макс. остаток, месяц 11', 'Макс. остаток, месяц 12', 'Комментарий, при необходимости2',
                'Категория'
              ]

    __tablename__ = 'tab_sh_ogr_bk'
    id = so.mapped_column(sa.Integer, primary_key=True, info={'display': '№'})
    tab_bazis_bk_ids = so.mapped_column(sa.String, info={'display': 'Базис отгрузки'})
    tab_product_bk_ids = so.mapped_column(sa.String, info={'display': 'Продукт'})
    tab_ei_bk_ids = so.mapped_column(sa.String, info={'display': 'Ед. изм.'})
    tab_proizv_bk_ids = so.mapped_column(sa.String, info={'display': 'Агент / производитель'})
    tab_sobstv_bk_ids = so.mapped_column(sa.String, info={'display': 'Собственник продукта'})
    min_jan = so.mapped_column(sa.String, info={'display': 'Мин. остаток, месяц 1'})
    min_feb = so.mapped_column(sa.String, info={'display': 'Мин. остаток, месяц 2'})
    min_mar = so.mapped_column(sa.String, info={'display': 'Мин. остаток, месяц 3'})
    min_apr = so.mapped_column(sa.String, info={'display': 'Мин. остаток, месяц 4'})
    min_may = so.mapped_column(sa.String, info={'display': 'Мин. остаток, месяц 5'})
    min_jun = so.mapped_column(sa.String, info={'display': 'Мин. остаток, месяц 6'})
    min_jul = so.mapped_column(sa.String, info={'display': 'Мин. остаток, месяц 7'})
    min_aug = so.mapped_column(sa.String, info={'display': 'Мин. остаток, месяц 8'})
    min_sep = so.mapped_column(sa.String, info={'display': 'Мин. остаток, месяц 9'})
    min_oct = so.mapped_column(sa.String, info={'display': 'Мин. остаток, месяц 10'})
    min_nov = so.mapped_column(sa.String, info={'display': 'Мин. остаток, месяц 11'})
    min_dec = so.mapped_column(sa.String, info={'display': 'Мин. остаток, месяц 12'})
    comment_min = so.mapped_column(sa.String, info={'display': 'Комментарий, при необходимости'})
    max_jan = so.mapped_column(sa.String, info={'display': 'Макс. остаток, месяц 1'})
    max_feb = so.mapped_column(sa.String, info={'display': 'Макс. остаток, месяц 2'})
    max_mar = so.mapped_column(sa.String, info={'display': 'Макс. остаток, месяц 3'})
    max_apr = so.mapped_column(sa.String, info={'display': 'Макс. остаток, месяц 4'})
    max_may = so.mapped_column(sa.String, info={'display': 'Макс. остаток, месяц 5'})
    max_jun = so.mapped_column(sa.String, info={'display': 'Макс. остаток, месяц 6'})
    max_jul = so.mapped_column(sa.String, info={'display': 'Макс. остаток, месяц 7'})
    max_aug = so.mapped_column(sa.String, info={'display': 'Макс. остаток, месяц 8'})
    max_sep = so.mapped_column(sa.String, info={'display': 'Макс. остаток, месяц 9'})
    max_oct = so.mapped_column(sa.String, info={'display': 'Макс. остаток, месяц 10'})
    max_nov = so.mapped_column(sa.String, info={'display': 'Макс. остаток, месяц 11'})
    max_dec = so.mapped_column(sa.String, info={'display': 'Макс. остаток, месяц 12'})
    comment_max = so.mapped_column(sa.String, info={'display': 'Комментарий, при необходимости2'})
    tab_category_product_bk_ids = so.mapped_column(sa.String, info={'display': 'Категория'})
    
class LeftoversTemplate(Base, BaseTemplate): # Шаблон Остатки
    START_ROW = 4
    SHEET_NAME = 'Остатки'
    COLUMNS = [
                '№', 'Месяц', 'Базис отгрузки', 'Продукт', 'Ед. изм.', 'Собственник продукта', 'Агент / производитель',
                'Остатки', 'Комментарий, при необходимости', 'Категория',
              ]
    
    __tablename__ = 'tab_sh_ost_bk'

    id = so.mapped_column(sa.Integer, primary_key=True, info={'display': '№'})
    month = so.mapped_column(sa.String, info={'display': 'Месяц'})
    tab_bazis_bk_ids = so.mapped_column(sa.String, info={'display': 'Базис отгрузки'})
    tab_product_bk_ids = so.mapped_column(sa.String, info={'display': 'Продукт'})
    tab_ei_bk_ids = so.mapped_column(sa.String, info={'display': 'Ед. изм.'})
    tab_proizv_bk_ids = so.mapped_column(sa.String, info={'display': 'Собственник продукта'})
    tab_sobstv_bk_ids = so.mapped_column(sa.String, info={'display': 'Агент / производитель'})
    ost = so.mapped_column(sa.String, info={'display': 'Остатки'})
    comment = so.mapped_column(sa.String, info={'display': 'Комментарий, при необходимости'})
    tab_category_product_bk_ids = so.mapped_column(sa.String, info={'display': 'Категория'})


class PlanTemplate(Base, BaseTemplate): # Шаблон План Производства
    START_ROW = 5
    SHEET_NAME = 'Пр-во'
    COLUMNS = [
                '№', 'Ед. изм.', 'Базис отгрузки', 'Продукт', 'Собственник продукта', 'Агент / производитель',
                'План пр-ва, месяц 1', 'План пр-ва, месяц 2', 'План пр-ва, месяц 3', 'План пр-ва, месяц 4',
                'План пр-ва, месяц 5', 'План пр-ва, месяц 6', 'План пр-ва, месяц 7', 'План пр-ва, месяц 8',
                'План пр-ва, месяц 9', 'План пр-ва, месяц 10', 'План пр-ва, месяц 11', 'План пр-ва, месяц 12',
                'Комментарий, при необходимости', 'Категория'
              ]
    
    __tablename__ = 'tab_sh_zayav_proizv_bk'

    id = so.mapped_column(sa.Integer, primary_key=True, info={'display': '№'})
    tab_bazis_bk_ids = so.mapped_column(sa.String, info={'display': 'Базис отгрузки'})
    tab_product_bk_ids = so.mapped_column(sa.String, info={'display': 'Продукт'})
    tab_ei_bk_ids = so.mapped_column(sa.String, info={'display': 'Ед. изм.'})
    tab_category_product_bk_ids = so.mapped_column(sa.String, info={'display': 'Категория'})
    tab_sobstv_bk_ids = so.mapped_column(sa.String, info={'display': 'Собственник продукта'})
    tab_proizv_bk_ids = so.mapped_column(sa.String, info={'display': 'Агент / производитель'})
    jan = so.mapped_column(sa.String, info={'display': 'План пр-ва, месяц 1'})
    feb = so.mapped_column(sa.String, info={'display': 'План пр-ва, месяц 2'})
    mar = so.mapped_column(sa.String, info={'display': 'План пр-ва, месяц 3'})
    apr = so.mapped_column(sa.String, info={'display': 'План пр-ва, месяц 4'})
    may = so.mapped_column(sa.String, info={'display': 'План пр-ва, месяц 5'})
    jun = so.mapped_column(sa.String, info={'display': 'План пр-ва, месяц 6'})
    jul = so.mapped_column(sa.String, info={'display': 'План пр-ва, месяц 7'})
    aug = so.mapped_column(sa.String, info={'display': 'План пр-ва, месяц 8'})
    sep = so.mapped_column(sa.String, info={'display': 'План пр-ва, месяц 9'})
    oct = so.mapped_column(sa.String, info={'display': 'План пр-ва, месяц 10'})
    nov = so.mapped_column(sa.String, info={'display': 'План пр-ва, месяц 11'})
    dec = so.mapped_column(sa.String, info={'display': 'План пр-ва, месяц 12'})
    comment = so.mapped_column(sa.String, info={'display': 'Комментарий, при необходимости'})