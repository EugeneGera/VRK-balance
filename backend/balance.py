# TODO! Раскомментить на деплое
##########################
# import sys
# import os

# sys.path.insert(0, 'opt/foresight')

##########################


import threading
from flask import Flask, Response, session


from app.config import Config

access_control_imported = True
try:
    from access_control_center.access_control_center_app import validate_requester
    from access_control_center.centrilized_database_pool import database_session_pool
except ImportError:
    access_control_imported = False

application = Flask(__name__)
application.config.from_object(Config)
application.config["JSON_SORT_KEYS"] = False
# cors только на деве. но он на проде и не нужен :)
try:
    from flask_cors import CORS
    CORS(application)
except ImportError:
    pass

if Config.DEPLOY_MODE == 'PROD' and access_control_imported:
    validate_requester(application)
    database_session_pool(application)
else:
    # TODO! возможно удалять на PROD
    @application.after_request
    def add_custom_header(response : Response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    def init_db():
        if Config.DEPLOY_MODE == 'local':

            # TODO! добавить модели
            ''' 
            from app.entities.models import Base, RegionModel, CategoryModel, FactoryModel, ProductModel, ShipmentModel, AgentPlanModel, TransportModel, FactoryTypeModel, ContractPlanModel
            
            Base.metadata.create_all(bind=engine)
            '''


    with application.app_context():
        init_db()





from flask_restx import Api

from app.apis.ns_sankey import ns_sankey
from app.apis.ns_info import ns_info
from app.apis.ns_journal import ns_journal
from app.apis.ns_loading import ns_loading
from app.apis.ns_directory import ns_directory


if Config.DEPLOY_MODE == 'PROD' and access_control_imported:
    validate_requester(application)
    database_session_pool(application)


# ADDING API NAMESPACES

api = Api(application,
          version='1.0',
          title='balance-comission API')

api.add_namespace(ns_sankey, path='/sankey')
api.add_namespace(ns_info)
api.add_namespace(ns_directory)
api.add_namespace(ns_journal, path='/journal')
api.add_namespace(ns_loading)


if Config.DEPLOY_MODE == 'local' and __name__ == '__main__' :
    application.run(host='0.0.0.0', port=5001, debug=Config.DEBUG)