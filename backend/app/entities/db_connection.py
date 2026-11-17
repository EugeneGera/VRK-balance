from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from flask import g

from app.config import Config

engine = create_engine(Config.DB_URI, pool_size=10, max_overflow=20)


def set_db_connection():
    if Config.DEPLOY_MODE == 'PROD':
        return g.session
    else:
        return scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()