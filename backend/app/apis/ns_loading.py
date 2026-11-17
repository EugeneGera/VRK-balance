from flask import request
from flask_restx import Namespace, Resource, reqparse
from datetime import datetime
from werkzeug.datastructures import FileStorage
from app.entities.db_connection import set_db_connection
from app.services.upload_service import UploadService
from app.apis.utils import exceptions_codes_docs, handle_exceptions
from app.core.errors import MissingFileException


ns_loading = Namespace('upload', description='Upload API')

loading_parser = reqparse.RequestParser()
loading_parser.add_argument('file', type=FileStorage, location='files', required=False, help='File is required')
loading_parser.add_argument('type', required=True, location='form', type=str, help='Type of upload: application, plan, leftovers or restrictions')
loading_parser.add_argument('year', required=False, location='form', type=int, default=datetime.now().year, help='year (current by default)')


@ns_loading.route('/applications', methods=['POST', 'PUT', 'OPTIONS'], endpoint='loading-applications')
class LoadingApplications(Resource):
   
    @ns_loading.expect(loading_parser)
    @ns_loading.response(200, 'Success')
    @ns_loading.response(404, 'Fail')
    @exceptions_codes_docs(ns_loading)
    @handle_exceptions
    def post(self):
        db_session = set_db_connection()

        args = loading_parser.parse_args()

        file : FileStorage = args['file']

        if not file or file.filename == '':
            raise MissingFileException()

        result = UploadService(db_session).upload_file(file=file, year=request.form['year'], file_type=request.form['type'])
        
        return result 
    
    def options(self):
        origin = request.headers.get('Origin')
        return {'Allow': 'PUT, POST'}, 200, {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': 'POST, PUT, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }