from flask import request
from flask_restx import Namespace, Resource, reqparse

from app.entities.db_connection import set_db_connection
from app.entities.schemas import FactoryDetailsSchema, month_details_list_schema
from app.apis.utils import get_months, sankey_parser_with_date, sankey_parser_with_date_mode
from app.services.shipments_service import ShipmentsService
# from app.services.utils import FilterSessionService

ns_sankey = Namespace('sankey', description='Sankey API')
# TODO! сделать один месяц
@ns_sankey.route('/graph', endpoint='sankey-graph')
@ns_sankey.expect(sankey_parser_with_date_mode)  
class SankeyGraph(Resource):
    @ns_sankey.response(200, 'Success')
    @ns_sankey.response(404, 'Fail')
    def get(self):
        db_session = set_db_connection()
        args = sankey_parser_with_date_mode.parse_args()

        shipments_service = ShipmentsService(db_session)
        months = get_months(args)#list(range(args['month_start'], args['month_end'] + 1))
        # FilterSessionService.update_product_filter(session=db_session,
        #                                                              year=args['year'], months=months,
        #                                                              basis_names=args['basises'],
        #                                                              product_names=args['product'],
        #                                                              category_names=args['category_product'])
        return shipments_service.get_sankey_data(
                                                year = args['year'],
                                                months=months,
                                                basises=args['basises'],
                                                products=args['product'],
                                                category_product=args['category_product'],
                                                grouping_base = args['grouping_mode']
                                                )

@ns_sankey.route('/waterfall', endpoint='waterfall')
@ns_sankey.expect(sankey_parser_with_date)  
class WaterfallGraph(Resource):
    @ns_sankey.response(200, 'Success')
    @ns_sankey.response(404, 'Fail')
    def get(self):
        db_session = set_db_connection()
        args = sankey_parser_with_date_mode.parse_args()

        shipments_service = ShipmentsService(db_session)
        months = get_months(args)#list(range(args['month_start'], args['month_end'] + 1))
        # FilterSessionService.update_product_filter(session=db_session,
        #                                                              year=args['year'], months=months,
        #                                                              basis_names=args['basises'],
        #                                                              product_names=args['product'],
        #                                                              category_names=args['category_product'])
        return {'data': {'data': shipments_service.get_waterfall(
                                            year = args['year'],
                                            months=months,
                                            basises=args['basises'],
                                            products=args['product'],
                                            category_product=args['category_product'],
                                            # grouping_base = args['grouping_mode']
                                            )},
                'unit': shipments_service.get_shipped_unit_names(year=args['year'],
                                                                 products=args['product'],
                                                                 category_product=args['category_product'],
                                                                 months=months,
                                                                 basises=args['basises'])
                }
        
@ns_sankey.route('/stock_details', endpoint='stock-details')
@ns_sankey.expect(sankey_parser_with_date) 
class StockMarket(Resource):
    @ns_sankey.response(200, 'Success')
    @ns_sankey.response(404, 'Fail')
    def get(self):
        db_session = set_db_connection()
        args = sankey_parser_with_date.parse_args()

        shipments_service = ShipmentsService(db_session)
        months = get_months(args)#list(range(args['month_start'], args['month_end'] + 1))

        return shipments_service.get_stock_details(
                                                year=args['year'],
                                                months=months,
                                                basises=args['basises'],
                                                products=args['product'],
                                                category_product=args['category_product']
                                                )
    
# deprecated
@ns_sankey.route('/transport_details', endpoint='transport-details')
@ns_sankey.expect(sankey_parser_with_date)  
class Transport(Resource):
    @ns_sankey.response(200, 'Success')
    @ns_sankey.response(404, 'Fail')
    def get(self):
        db_session = set_db_connection()
        args = sankey_parser_with_date.parse_args()

        shipments_service = ShipmentsService(db_session)
        months = get_months(args, 3)#list(range(args['month_start'], args['month_end'] + 1))[:min(args['month_end'] - args['month_start'] + 1, 3)]
        # FilterSessionService.update_product_filter(session=db_session,
        #                                                              year=args['year'], months=months,
        #                                                              basis_names=args['basises'],
        #                                                              product_names=args['product'],
        #                                                              category_names=args['category_product'])
        data = shipments_service.get_transport_details(
                                                year = args['year'],
                                                months=months,
                                                basises=args['basises'],
                                                products=args['product'],
                                                category_product=args['category_product']
                                                )

        return month_details_list_schema.dump({'months': data['months']})

@ns_sankey.route('/factory_details', endpoint='factory-details')
@ns_sankey.expect(sankey_parser_with_date)  
class Factory(Resource):
    @ns_sankey.response(200, 'Success')
    @ns_sankey.response(404, 'Fail')
    def get(self):
        db_session = set_db_connection()
        args = sankey_parser_with_date.parse_args()

        shipments_service = ShipmentsService(db_session)
        months = get_months(args, 3)#list(range(args['month_start'], args['month_end'] + 1))[:min(args['month_end'] - args['month_start'] + 1, 3)]

        # FilterSessionService.update_product_filter(session=db_session,
        #                                                              year=args['year'], months=months,
        #                                                              basis_names=args['basises'],
        #                                                              product_names=args['product'],
        #                                                              category_names=args['category_product'])
        data = shipments_service.get_factory_details(
                                                year = args['year'],
                                                months=months,
                                                basises=args['basises'],
                                                products=args['product'],
                                                category_product=args['category_product']
                                                )
        
        return FactoryDetailsSchema().dump(data)

@ns_sankey.route('/table', endpoint='table')
@ns_sankey.expect(sankey_parser_with_date)
class SankeyTable(Resource):
    @ns_sankey.response(200, 'Success')
    @ns_sankey.response(404, 'Fail')
    def get(self):
        db_session = set_db_connection()
        args = sankey_parser_with_date.parse_args()

        shipments_service = ShipmentsService(db_session)
        months = get_months(args, 3)

        data = shipments_service.get_table(
            year=args['year'],
            months=months,
            basises=args['basises'],
            products=args['product'],
            category_product=args['category_product'],
        )

        try:
            decimals = int(request.args.get('decimals', 2))
        except (TypeError, ValueError):
            decimals = 2
        dash_zero = str(request.args.get('dash_zero', '1')).lower() not in ('0', 'false', 'no')
        eps = float(request.args.get('zero_epsilon', '1e-12'))

        def fmt_cell(x, is_name_col: bool):
            if is_name_col:
                return x
            if isinstance(x, (int, float)):
                v = float(x)
                if dash_zero and abs(v) <= eps:
                    return '—'
                return f'{round(v, decimals):.{decimals}f}'
            return x

        data = [
            [fmt_cell(cell, is_name_col=(idx == 0)) for idx, cell in enumerate(row)]
            for row in data
        ]

        return data
        
@ns_sankey.route('/factory_income', endpoint='factory-income')
@ns_sankey.expect(sankey_parser_with_date) 
class FactoryIncome(Resource):
    @ns_sankey.response(200, 'Success')
    @ns_sankey.response(404, 'Fail')
    def get(self):
        db_session = set_db_connection()
        args = sankey_parser_with_date.parse_args()

        shipments_service = ShipmentsService(db_session)
        months = get_months(args)#list(range(args['month_start'], args['month_end'] + 1))

        # FilterSessionService.update_product_filter(session=db_session,
        #                                                              year=args['year'], months=months,
        #                                                              basis_names=args['basises'],
        #                                                              product_names=args['product'],
        #                                                              category_names=args['category_product'])
        data = shipments_service.get_factory_income(
                                        year = args['year'],
                                        months=months,
                                        basises=args['basises'],
                                        products=args['product'],
                                        category_product=args['category_product']
                                        )
        return data