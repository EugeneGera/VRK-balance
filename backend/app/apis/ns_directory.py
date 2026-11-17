from flask import request
from flask_restx import Namespace, Resource, fields

from app.entities.db_connection import set_db_connection
from app.services.directory_service import DirectoryService
from app.apis.utils import handle_exceptions


ns_directory = Namespace("directories", description='Directories API')

directory_model = ns_directory.model("DirectoryModel", {
    "id": fields.Integer(required=True, description='id', example=1, min=1),
    "name": fields.String(required=True, description='name')
})

directory_update_model_list = ns_directory.model(
    "DirectoryList", {'directories': fields.List(fields.Nested(directory_model))})


@ns_directory.route('', endpoint='directories')
class Directories(Resource):
    @ns_directory.response(200, "Success")
    @ns_directory.response(400, "Fail")
    def get(self):
        db_session = set_db_connection()
        return DirectoryService(db_session).get_directories_list()


@ns_directory.route('/<string:tablename>', endpoint='directory')
class Directory(Resource):
    @ns_directory.response(200, "Success")
    @ns_directory.response(400, "Fail")
    def get(self, tablename):
        db_session = set_db_connection()
        return DirectoryService(db_session).get_directory_by_tablename(tablename)

    @ns_directory.expect(directory_update_model_list)
    @ns_directory.response(200, 'Success')
    @ns_directory.response(404, 'Fail')
    @handle_exceptions
    def put(self, tablename):
        db_session = set_db_connection()
        data = request.get_json("directories")
        result = DirectoryService(db_session).update_directory(tablename, data["directories"])
        return result


    def options(self, **kwargs):
        origin = request.headers.get('Origin')
        return {'Allow': 'PUT'}, 200, {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': 'PUT, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
