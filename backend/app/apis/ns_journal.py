from flask import abort, request, jsonify
from flask_restx import Namespace, Resource, reqparse, fields
from datetime import datetime

from app.entities.db_connection import set_db_connection
from app.services.application_service import ApplicationService
from app.services.plan_service import PlanService
from app.services.leftover_service import LeftoverService
from app.services.limit_service import LimitService
from app.entities.schemas import ApplicationUpdateSchema, PlanUpdateSchema, LeftoverUpdateSchema, LimitUpdateSchema


ns_journal = Namespace('journal', description='Journal API')

# applications
journal_parser = reqparse.RequestParser()
journal_parser.add_argument('year', required=False, type=int, default=datetime.now().year, help='year (current by default)')
journal_parser.add_argument('month_start', required=False, type=int, default=datetime.now().month, help='month (current by default)')
journal_parser.add_argument('month_end', required=False, type=int, default=datetime.now().month, help='month (current by default)')
journal_parser.add_argument('category_product', required=False, type=str, help='comma separated list of product categories (default: Any)', action='split')
journal_parser.add_argument('product', required=False, type=str, help='product (default: Any)', action='split')
journal_parser.add_argument('basises', required=False, type=str, 
                            help='comma separated list of factories', action='split')
journal_parser.add_argument('hide_zero', type=lambda x: x.lower() == 'true', help='hide zero (true/false)', default=False)

application_model = ns_journal.model('Application', {
    'id': fields.Integer(required=True,description='id',example=1,min=1),
    'applicationSize': fields.Float(description='value',example=1024.5),
    'price': fields.Float(description='price',example=99.99),
    'remark': fields.String(description='comment',example="text test"),
})

application_update_model = ns_journal.model('ApplicationUpdate', {
    'application': fields.Nested(application_model,required=True)
})

# Модель для списка заявки
application_list_update_model = ns_journal.model('ApplicationsList', {
    'applications': fields.List(fields.Nested(application_model), 
                         required=True,
                         description='Список заявок')
})

@ns_journal.route('/applications', methods=['GET', 'PUT', 'OPTIONS'], endpoint='applications')
class Applications(Resource):
    @ns_journal.expect(journal_parser)
    @ns_journal.response(200, 'Success')
    @ns_journal.response(404, 'Fail')
    def get(self):
        try:
            args = journal_parser.parse_args()
            db_session = set_db_connection()
            filters = args.copy()#{}
            filters['months'] = list(range(args['month_start'], args['month_end'] + 1))
            result = ApplicationService(db_session).get_data(filters)
        except Exception as err:
            ns_journal.logger.error(f"error: {str(err)}")
            # return {"errors": str(err)}, 400
            raise

        return result
    
    @ns_journal.expect(application_list_update_model)
    @ns_journal.response(200, 'Success')
    @ns_journal.response(404, 'Fail')
    def put(self):
        try:
            data = request.get_json()
            applicationsUpdateData = ApplicationUpdateSchema(many=True).load(data["applications"])
            db_session = set_db_connection()
            result = ApplicationService(db_session).update_data(applicationsUpdateData)
        except Exception as err:
            ns_journal.logger.error(f"error: {str(err)}")
            #return {"errors": str(err)}, 400
            raise
        
        return result 
    
    def options(self):
        origin = request.headers.get('Origin')
        return {'Allow': 'PUT'}, 200, {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': 'PUT, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }   
    


# @ns_journal.route('/application', methods=['PUT', 'OPTIONS'], endpoint='application')
# class Application(Resource):
#     @cross_origin()
#     @ns_journal.expect(application_update_model)
#     @ns_journal.response(200, 'Success')
#     @ns_journal.response(404, 'Fail')
#     def put(self):
#         try:
#             data = request.get_json()
#             applicationUpdateData = ApplicationUpdateSchema().load(data["application"])
#             db_session = set_db_connection()
#             result = ApplicationService(db_session).update_data(applicationUpdate=applicationUpdateData)
#         except Exception as err:
#             ns_journal.logger.error(f"error: {str(err)}")
#             #return {"errors": str(err)}, 400
#             raise
        
#         return result
    
#     def options(self):
#         origin = request.headers.get('Origin')
#         return {'Allow': 'PUT'}, 200, {
#             'Access-Control-Allow-Origin': origin,
#             'Access-Control-Allow-Methods': 'PUT, OPTIONS',
#             'Access-Control-Allow-Headers': 'Content-Type, Authorization'
#         }
             
# plans   
plan_model = ns_journal.model('Plan', {
    'id': fields.Integer(required=True,description='id',example=1,min=1),
    'plan': fields.Float(description='plan',example=200),
    # 'min_left': fields.Float(description='min_left',example=50),
    # 'max_shipment': fields.Float(description='max_shipment',example=300)
    'remark': fields.String(description='comment',example="text test"),
})

plan_update_model = ns_journal.model('PlanUpdate', {
    'plan': fields.Nested(plan_model,required=True)
})

# Модель для списка планов
plans_list_update_model = ns_journal.model('PlansList', {
    'plans': fields.List(fields.Nested(plan_model), 
                         required=True,
                         description='Список планов')
})

@ns_journal.route('/plans', methods=['GET', 'PUT', 'OPTIONS'], endpoint='plans')
class Plans(Resource):
    @ns_journal.expect(journal_parser)
    @ns_journal.response(200, 'Success')
    @ns_journal.response(404, 'Fail')
    def get(self):
        try:
            args = journal_parser.parse_args()
            db_session = set_db_connection()
            filters = args.copy()#{}
            filters['months'] = list(range(args['month_start'], args['month_end'] + 1))
            result = PlanService(db_session).get_data(filters)
        except Exception as err:
            ns_journal.logger.error(f"error: {str(err)}")
            # return {"errors": str(err)}, 400
            raise

        return result
    
    @ns_journal.expect(plans_list_update_model)
    @ns_journal.response(200, 'Success')
    @ns_journal.response(404, 'Fail')
    def put(self):
        try:
            data = request.get_json()
            plansUpdateData = PlanUpdateSchema(many=True).load(data["plans"])
            db_session = set_db_connection()
            result = PlanService(db_session).update_data(plansUpdateData)
        except Exception as err:
            ns_journal.logger.error(f"error: {str(err)}")
            #return {"errors": str(err)}, 400
            raise
        
        return result 
    
    def options(self):
        origin = request.headers.get('Origin')
        return {'Allow': 'PUT'}, 200, {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': 'PUT, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }    

# @ns_journal.route('/plan', methods=['PUT', 'OPTIONS'], endpoint='plan')
# class Plan(Resource):
#     @cross_origin()
#     @ns_journal.expect(plan_update_model)
#     @ns_journal.response(200, 'Success')
#     @ns_journal.response(404, 'Fail')
#     def put(self):
#         try:
#             data = request.get_json()
#             planUpdateData = PlanUpdateSchema().load(data["plan"])
#             db_session = set_db_connection()
#             result = PlanService(db_session).update_data(planUpdate=planUpdateData)
#         except Exception as err:
#             ns_journal.logger.error(f"error: {str(err)}")
#             #return {"errors": str(err)}, 400
#             raise
        
#         return result  

#     def options(self):
#         origin = request.headers.get('Origin')
#         return {'Allow': 'PUT'}, 200, {
#             'Access-Control-Allow-Origin': origin,
#             'Access-Control-Allow-Methods': 'PUT, OPTIONS',
#             'Access-Control-Allow-Headers': 'Content-Type, Authorization'
#         }      

# leftovers
leftover_model = ns_journal.model('Leftover', {
    'id': fields.Integer(required=True,description='id',example=1,min=1),
    'left': fields.Float(description='left',example=100),
    # 'plan': fields.Float(description='plan',example=200),
    # 'min_left': fields.Float(description='min_left',example=50),
    # 'max_shipment': fields.Float(description='max_shipment',example=300),
    'remark': fields.String(description='comment',example="text test"),
})

leftover_update_model = ns_journal.model('LeftoverUpdate', {
    'leftover': fields.Nested(leftover_model,required=True)
})

# Модель для списка планов
leftovers_list_update_model = ns_journal.model('LeftoversList', {
    'leftovers': fields.List(fields.Nested(leftover_model), 
                         required=True,
                         description='Список остатки')
})

@ns_journal.route('/leftovers', methods=['GET', 'PUT', 'OPTIONS'], endpoint='leftovers')
class Leftovers(Resource):
    @ns_journal.expect(journal_parser)
    @ns_journal.response(200, 'Success')
    @ns_journal.response(404, 'Fail')
    def get(self):
        try:
            args = journal_parser.parse_args()
            db_session = set_db_connection()
            filters = args.copy()#{}
            filters['months'] = list(range(args['month_start'], args['month_end'] + 1))
            result = LeftoverService(db_session).get_data(filters)
        except Exception as err:
            ns_journal.logger.error(f"error: {str(err)}")
            # return {"errors": str(err)}, 400
            raise

        return result
    
    @ns_journal.expect(leftovers_list_update_model)
    @ns_journal.response(200, 'Success')
    @ns_journal.response(404, 'Fail')
    def put(self):
        try:
            data = request.get_json()
            plansUpdateData = LeftoverUpdateSchema(many=True).load(data["leftovers"])
            db_session = set_db_connection()
            result = LeftoverService(db_session).update_data(plansUpdateData)
        except Exception as err:
            ns_journal.logger.error(f"error: {str(err)}")
            #return {"errors": str(err)}, 400
            raise
        
        return result 
    
    def options(self):
        origin = request.headers.get('Origin')
        return {'Allow': 'PUT'}, 200, {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': 'PUT, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }

# limits
limit_model = ns_journal.model('Limit', {
    'id': fields.Integer(required=True,description='id',example=1,min=1),
    'min_left': fields.Float(description='min_left',example=50),
    'min_remark': fields.String(description='comment',example="text 1"),
    'max_shipment': fields.Float(description='max_shipment',example=300),
    'max_remark': fields.String(description='comment',example="text 2")
})

limit_update_model = ns_journal.model('limitUpdate', {
    'limit': fields.Nested(limit_model,required=True)
})

# Модель для списка лимитов
limits_list_update_model = ns_journal.model('limitsList', {
    'limits': fields.List(fields.Nested(limit_model), 
                         required=True,
                         description='Список ограничений')
})

@ns_journal.route('/limits', methods=['GET', 'PUT', 'OPTIONS'], endpoint='limits')
class Limits(Resource):
    @ns_journal.expect(journal_parser)
    @ns_journal.response(200, 'Success')
    @ns_journal.response(404, 'Fail')
    def get(self):
        try:
            args = journal_parser.parse_args()
            db_session = set_db_connection()
            filters = args.copy()#{}
            filters['months'] = list(range(args['month_start'], args['month_end'] + 1))
            result = LimitService(db_session).get_data(filters)
        except Exception as err:
            ns_journal.logger.error(f"error: {str(err)}")
            # return {"errors": str(err)}, 400
            raise

        return result
    
    @ns_journal.expect(limits_list_update_model)
    @ns_journal.response(200, 'Success')
    @ns_journal.response(404, 'Fail')
    def put(self):
        try:
            data = request.get_json()
            limitsUpdateData = LimitUpdateSchema(many=True).load(data["limits"])
            db_session = set_db_connection()
            result = LimitService(db_session).update_data(limitsUpdateData)
        except Exception as err:
            ns_journal.logger.error(f"error: {str(err)}")
            #return {"errors": str(err)}, 400
            raise
        
        return result 
    
    def options(self):
        origin = request.headers.get('Origin')
        return {'Allow': 'PUT'}, 200, {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': 'PUT, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }