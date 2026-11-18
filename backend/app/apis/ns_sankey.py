from flask import request
from flask_restx import Namespace, Resource
from app.analytics.legacy import BalancePresentation
from app.analytics.transport import read_endpoint
from app.apis.utils import sankey_parser_with_date_mode, get_months
from app.services.shipments_service import ShipmentsService
from app.entities.schemas import FactoryDetailsSchema

ns_sankey = Namespace('sankey', description='Dashboard presentation of the common balance calculator')


def arguments():
    args = sankey_parser_with_date_mode.parse_args()
    get_months(args)
    for key in ('decimals', 'dash_zero'):
        if key in request.args:
            args[key] = request.args[key]
    return args


@ns_sankey.route('/waterfall')
class Waterfall(Resource):
    @read_endpoint('ui.waterfall', protected=False)
    def get(self, session, principal):
        return BalancePresentation(session, arguments()).waterfall()


@ns_sankey.route('/table')
class BalanceTable(Resource):
    @read_endpoint('ui.table', protected=False)
    def get(self, session, principal):
        return BalancePresentation(session, arguments()).table()


@ns_sankey.route('/stock_details')
class Stock(Resource):
    @read_endpoint('ui.stock_details', protected=False)
    def get(self, session, principal):
        return BalancePresentation(session, arguments()).stock()


@ns_sankey.route('/graph')
class Graph(Resource):
    @read_endpoint('ui.graph', protected=False)
    def get(self, session, principal):
        return BalancePresentation(session, arguments()).graph()


@ns_sankey.route('/factory_details')
class FactoryDetails(Resource):
    @read_endpoint('ui.factory_details', protected=False)
    def get(self, session, principal):
        args = arguments()
        view = BalancePresentation(session, args)
        result = ShipmentsService(session).get_factory_details(year=args['year'], months=get_months(args),
                    basises=args['basises'], products=args['product'], category_product=args['category_product'])
        return view.finish(FactoryDetailsSchema().dump(result), len(result))


@ns_sankey.route('/transport_details')
class TransportDetails(Resource):
    def get(self):
        return {'error': {'code': 'unsupported_operation', 'message': 'Устаревший транспортный API не поддерживается; используйте аналитический API.'}}, 410


@ns_sankey.route('/factory_income')
class FactoryIncome(Resource):
    @read_endpoint('ui.factory_income', protected=False)
    def get(self, session, principal):
        args = arguments()
        view = BalancePresentation(session, args)
        result = ShipmentsService(session).get_factory_income(year=args['year'], months=get_months(args),
                    basises=args['basises'], products=args['product'], category_product=args['category_product'])
        return view.finish(result, len(result))
