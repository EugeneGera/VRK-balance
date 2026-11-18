import re
from sqlalchemy import text
from sqlalchemy.orm import scoped_session


def execute_sql_file(sql_file_path: str, session: scoped_session, **kwargs):
    with open(sql_file_path, 'r', encoding='utf-8-sig') as file:
        sql_script = file.read()
    
    # Удаление комментов
    sql_script = re.sub(r'--.*?\n', '', sql_script)  
    sql_script = re.sub(r'\/\/.*?\n', '', sql_script) 
    sql_script = re.sub(r'/\*.*?\*/', '', sql_script, flags=re.DOTALL) 
    
    # Отдельные стейтменты
    statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
    
    connection = session.connection()
    
    try:
        for stmt in statements:
            if stmt[-1] != ';':
                 stmt += ';'
            if stmt:  # минус пустые строки
                connection.execute(text(stmt), kwargs)
        session.commit()  
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
