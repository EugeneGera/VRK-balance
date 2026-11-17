import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    UPLOAD_FOLDER = '/opt/foresight/balance_comission_back/uploads'
    JSON_AS_ASCII = False
    DEBUG = False


    DEPLOY_MODE = 'local' # local, PRUV, DEV, TEST, PROD


    if DEPLOY_MODE == 'local':
        DB_URI = os.environ.get('DATABASE_URL') or \
            'postgresql+psycopg2://postgres:postgres@localhost:5431/balance_comission'
        
        REDIS_HOST = os.environ.get('REDIS_HOST') or \
            'redis'
        REDIS_USER = os.environ.get('REDIS_USER') or \
            'redis'
        REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD') or \
            'redis'
        REDIS_PORT = os.environ.get('REDIS_PORT') or \
            6379
        REDIS_CHANNEL = 'oss_sse_channel'

        UPLOAD_FOLDER = './uploads/'
        DEBUG = True

    if DEPLOY_MODE == 'PRUV':
        DB_URI = 'postgresql://ISKAOGAZ:ISKAOGAZ@pruv-fsdev-db1.codm.gazprom.loc:10265/ISKAOGAZ'
    
    if DEPLOY_MODE == 'DEV':
        DB_URI = f'postgresql+psycopg2://IS_KAO:Gamma12345%Beta6789%25@kao-dev-db01.codm.gazprom.loc:5433/ISKAO_DATA'

    if DEPLOY_MODE == 'TEST':
        DATABASE = '@kao-qas-db01.codm.gazprom.loc'
        PASSWORD = 'Beta12345%Gamma6789#'
        USER = 'IS_KAO'
        PORT = '5433'
        DB_URI = f'postgresql://{USER}:{PASSWORD}{DATABASE}:{PORT}/ISKAO_DATA'

    if DEPLOY_MODE == 'PROD':
        SWAGGER_LINK = 'https://kao-prd-bal03/balance_comission/' # TODO не забыть поменять при деплое на прод
        FRONTEND_LINK  = 'https://kao-prd-bal03/balance_comission/' # TODO не забыть поменять при деплое на прод
        DATABASE_MODE = 'DIRECT' # DIRECT OR DOMAIN depending on authentiication mode
        AUTHORIZATION_MODE = 'DOMAIN'
        SERVERBASE_MODE = 'WSGI'
        UPLOAD_FOLDER = '/opt/foresight/apple/uploads'
        REDIS_PORT = 6379