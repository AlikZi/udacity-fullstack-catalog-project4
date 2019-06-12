class Config():
    SECRET_KEY = 'super_secret_key'
    DEBUG = False


class DevelopmentConfig(Config):
	DEBUG = True

class ProductionConfig(Config):
	DEBUG = False
