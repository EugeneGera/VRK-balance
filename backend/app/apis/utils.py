from datetime import datetime
from functools import wraps
from typing import Dict, List, Optional
from flask import jsonify
from flask_restx import Namespace, reqparse

from app.core.errors import CalculationFailException, FileDeletionException, FileSavingException, IncorrectFileFormatException, InvalidUploadTypeException, MissingFileException

sankey_parser = reqparse.RequestParser()
sankey_parser.add_argument('product', required=False, type=str, help='comma separated list of products (default: Any)', action='split')
sankey_parser.add_argument('category_product', required=False, type=str, help='comma separated list of product categories (default: Any)', action='split')
sankey_parser.add_argument('basises', required=False, type=str, 
                            help='comma separated list of factories', action='split')

sankey_parser_with_date = sankey_parser.copy()
sankey_parser_with_date.add_argument('year', required=False, type=int, default=datetime.now().year, help='year (current by default)')
sankey_parser_with_date.add_argument('month_start', required=False, type=int, default=datetime.now().month, help='month (current by default)')
sankey_parser_with_date.add_argument('month_end', required=False, type=int, default=None, help='last month, inclusive (defaults to month_start)')

sankey_parser_with_date_mode = sankey_parser_with_date.copy()
sankey_parser_with_date_mode.add_argument('grouping_mode', required=False, type=str, default='factories', help='sankey grouping mode (\'factories\' by default or \'products\')')
directory_parcer = reqparse.RequestParser()
directory_parcer.add_argument("id", required=False, type=int, help="id (for current directory)" )


EXCEPTIONS_RESOLVER = {
    IncorrectFileFormatException: {
        'code': 511,
        'msg': 'Неправильный формат загруженного файла'
    },
    FileSavingException: {
        'code': 512,
        'msg': 'Ошибка сохранения'
    },
    InvalidUploadTypeException: {
        'code': 513,
        'msg': 'Неправильный тип выгрузки'
    },
    CalculationFailException: {
        'code': 514,
        'msg': 'Ошибка запуска скрипта'
    },
    MissingFileException: {
        'code': 515,
        'msg': 'Файл не был загружен'
    },
    FileDeletionException: {
        'code': 516,
        'msg': 'Ошибка удаления файлов'
    },
    None: {
        'code': 517,
        'msg': 'Неизвестная ошибка сервера'
    }
}

def handle_exceptions(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # import traceback
            # print(traceback.format_exc())
            exception_type = type(e)

            if exception_type in EXCEPTIONS_RESOLVER:
                info = EXCEPTIONS_RESOLVER[exception_type]
            else:
                info = EXCEPTIONS_RESOLVER[None]
            print(e)
            return {
                'code': info['code'],
                'message': info['msg'],
                'logs': repr(e)
            }, info['code']
    return wrap
        
def exceptions_codes_docs(ns: Namespace, codes : Optional[List[int]] = None):
    def wrap(func):
        for exc, info in EXCEPTIONS_RESOLVER.items():
            if codes and info['code'] not in codes:
                continue
            func = ns.response(info['code'], info['msg'])(func)

        return func
    return wrap
            

def get_months(args: Dict, limit: Optional[int] = None):
    from app.analytics.contracts import Period
    values = {key: args[key] for key in ('year', 'month_start', 'month_end') if args.get(key) is not None}
    return list(Period.parse(values).months)
