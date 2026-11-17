from app.services.utils import execute_sql_file
from sqlalchemy.orm import scoped_session
from sqlalchemy import text
import threading

lock = threading.Lock()

class RecalculateRepository():   
    FULL_RECALC_SQL = 'backend/app/src/year_calc.sql'
    def __init__(self, session: scoped_session):
                self.session = session
                
    
    def recalculate(self, year:int):
           execute_sql_file(year=year, sql_file_path=self.FULL_RECALC_SQL, session=self.session)