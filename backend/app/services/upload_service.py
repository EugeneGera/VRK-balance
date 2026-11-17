from datetime import datetime
import os
import random
import string
import zipfile
from openpyxl import load_workbook
from typing import List
import os
from os.path import isfile

from sqlalchemy.orm import scoped_session

from app.entities.templates import BaseTemplate, LeftoversTemplate, PlanTemplate, RestrictionsTemplate, TransApplicationTemplate
from app.config import Config
from app.services.utils import execute_sql_file
from app.core.errors import CalculationFailException, FileDeletionException, FileSavingException, IncorrectFileFormatException, InvalidUploadTypeException

ALLOWED_ARCHIVE_FORMATS = ['zip']
ALLOWED_FILE_FORMATS = ['.xls', 'xlsx', 'xlsm']

def is_allowed_format(filename: str, formats: List):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in formats


class UploadService:
    def __init__(self, session: scoped_session):
        self.session = session
        self.TRANS_APPLICATIONS_CALC_SQL = "backend/app/src/trans_applications_calc.sql"
        self.PLAN_CALC_SQL = "backend/app/src/plan_calc.sql"
        self.LEFTOVERS_CALC_SQL = "backend/app/src/leftovers_calc.sql"
        self.RESTRICTIONS_CALC_SQL = "backend/app/src/restrictions_calc.sql"
        self.FULL_RECALC_SQL = "backend/app/src/year_calc.sql"

    def upload_file(self, file, year: int, file_type: str):
        self._clean_uploads()
        self._uploaded_file_names = []
        self._year = year
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

        if not file or not is_allowed_format(file.filename, ALLOWED_ARCHIVE_FORMATS + ALLOWED_FILE_FORMATS) :
             raise IncorrectFileFormatException(ALLOWED_ARCHIVE_FORMATS + ALLOWED_FILE_FORMATS)
        
        try:
            # Генерируем префикс имени файла: timestamp (ms) + рандомная строка
            # Нужно, потому что в папке загрузок не создаётся отдельный каталог для наших выгрузок..
            timestamp_ms = int(datetime.now().timestamp() * 1000)
            random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            self._file_prefix = f"{timestamp_ms}_{random_str}_"


            safe_filename = self._file_prefix + file.filename # имя файла с префиксом для сохранения

            filepath = os.path.join(Config.UPLOAD_FOLDER, safe_filename)
            file.save(filepath)

            self._uploaded_file_names = []
            if is_allowed_format(file.filename, ALLOWED_FILE_FORMATS):
                self._uploaded_file_names.append(safe_filename)

            if is_allowed_format(file.filename, ALLOWED_ARCHIVE_FORMATS):
                    # with zipfile.ZipFile(filepath, 'r') as archive:
                    #     archive.extractall(Config.UPLOAD_FOLDER)

                    # файлы выгружаются из архива с тем же префиксом
                    with zipfile.ZipFile(filepath, 'r') as archive:
                        for member in archive.namelist():
                            if not member.endswith('/') and not os.path.basename(member).startswith('.'):
                                member_filename = self._file_prefix + os.path.basename(member)
                                member_path = os.path.join(Config.UPLOAD_FOLDER, member_filename)
                                
                                os.makedirs(os.path.dirname(member_path), exist_ok=True)
                                
                                with archive.open(member) as source, open(member_path, 'wb') as target:
                                    target.write(source.read())
                                    self._uploaded_file_names.append(member_filename)
        except Exception as e:
            raise FileSavingException(repr(e))
        # print('uploaded', self._uploaded_file_names)
        if file_type == "application":
            self._upload_template(template_model=TransApplicationTemplate, sql_script_path=self.TRANS_APPLICATIONS_CALC_SQL)
        elif file_type == "plan":
            self._upload_template(template_model=PlanTemplate, sql_script_path=self.PLAN_CALC_SQL)
        elif file_type == "leftovers":
            self._upload_template(template_model=LeftoversTemplate, sql_script_path=self.LEFTOVERS_CALC_SQL) 
        elif file_type == "restrictions":
            self._upload_template(template_model=RestrictionsTemplate, sql_script_path=self.RESTRICTIONS_CALC_SQL)
        else:
            raise InvalidUploadTypeException(file_type)
        
        # TODO! нужно ли запускать перерасчёт года каждый раз?
        try:
            return execute_sql_file(year=self._year, sql_file_path=self.FULL_RECALC_SQL, session=self.session)
        except Exception as e:
            # print(f'upload_file error {self.FULL_RECALC_SQL}\n{e}')
            raise CalculationFailException(f'Error uploading file {self.FULL_RECALC_SQL}:\n{repr(e)}')
    

    def _upload_template(self, template_model: BaseTemplate, sql_script_path: str):
        data_models = []
        for filename in self._uploaded_file_names:
            if not is_allowed_format(filename, ALLOWED_FILE_FORMATS):
                continue
            
            file_path = os.path.join(Config.UPLOAD_FOLDER, filename)

            wb = load_workbook(filename=file_path, read_only=True, data_only=True)
            sheet = wb[template_model.SHEET_NAME]

            

            header_row = [cell.value.replace('\n', ' ') for cell in sheet[template_model.START_ROW] if cell.value is not None]
            # print(header_row)
            for row in sheet.iter_rows(min_row=template_model.START_ROW + 1, values_only=True):
                if len(row) == 0 or not row or not row[0]: # скипаем если первое значение пустое = пустая строка
                    continue
                data = {col: row[idx] if row[idx] != '' else None 
                            for idx, col in enumerate(header_row)}#[:len(row)])}
                data_model = template_model.create_from_row(data)
                data_model.id = len(data_models)
                # print(data_model)
                data_models.append(data_model)

            # Очищаем таблицу шаблона от старых записей
            self.session.query(template_model).delete()
            self.session.commit()
            
            # Добавляем все записи в сессию
        try:
            self.session.add_all(data_models)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        wb.close()
        
        try:
            execute_sql_file(year=self._year, sql_file_path=sql_script_path, session=self.session)
        except Exception as e:
            raise(CalculationFailException(f'Error uploading template {self.FULL_RECALC_SQL}:\n{repr(e)}'))

        return {}
    
    def _clean_uploads(self):
        error_files = []
        for file_name in os.listdir(Config.UPLOAD_FOLDER):#self._uploaded_file_names:
            file_path = os.path.join(Config.UPLOAD_FOLDER, file_name)
            if not isfile(file_path):
                continue
            try:
                os.remove(file_path)
            except Exception:
                error_files.append(file_name)
        if len(error_files) != 0:
            raise FileDeletionException(error_files)
