

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    JWT_SECRET_KEY = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'
    SECRET_KEY = '57e19ea558d4967a552d03deece34a70'
class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    ENV="development"
    DEVELOPMENT=True
    DEBUG=True
