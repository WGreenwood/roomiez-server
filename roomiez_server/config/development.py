from .base import ConfigBase


class DevelopmentConfig(ConfigBase):
    # Example with password
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:password@localhost:3306/roomiez_dev'
    SQLALCHEMY_DATABASE_URI = 'mysql://root@localhost:3306/roomiez_dev'
    DEBUG = True
    TESTING = False
