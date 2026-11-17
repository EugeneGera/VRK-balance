from flask_restx import Namespace, Resource

from app.entities.db_connection import set_db_connection
from app.services.info_service import InfoService
from app.apis.utils import get_months, sankey_parser_with_date

ns_info = Namespace('info', description='Dict and other info API')

@ns_info.route('/latest_period', endpoint='latest-period')
class LatestPeriod(Resource):
    @ns_info.response(200, 'Latest populated dashboard period, or null if no data is available')
    def get(self):
        db_session = set_db_connection()
        try:
            return InfoService(db_session).get_latest_period()
        finally:
            db_session.close()

@ns_info.route('/products', endpoint='products')
@ns_info.expect(sankey_parser_with_date)  
class ProductsList(Resource):
    @ns_info.response(200, 'Success')
    @ns_info.response(404, 'Fail')
    def get(self):
        args = sankey_parser_with_date.parse_args()
        db_session = set_db_connection()
        return InfoService(db_session).get_products_names_filtered(category_product=args['category_product'])

@ns_info.route('/category_product', endpoint='category_product')
@ns_info.expect(sankey_parser_with_date)
class CategoryProductsList(Resource):
    @ns_info.response(200, 'Success')
    @ns_info.response(404, 'Fail')
    def get(self):
        db_session = set_db_connection()
        return InfoService(db_session).get_category_product_names()

@ns_info.route('/shipping_basises', endpoint='shipping-basises')
@ns_info.expect(sankey_parser_with_date)  
class BasisesList(Resource):
    @ns_info.response(200, 'Success')
    @ns_info.response(404, 'Fail')
    def get(self):
        args = sankey_parser_with_date.parse_args()

        # months = list(range(args['month_start'], args['month_end'] + 1))
        months = get_months(args)
        db_session = set_db_connection()
        return InfoService(db_session).get_basises_names_filtered(year = args['year'],
                                                                  months = months,
                                                                  product_categories=args['category_product'])
