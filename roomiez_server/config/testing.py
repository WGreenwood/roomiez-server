from .base import ConfigBase


class TestingConfig(ConfigBase):
    SECRET_KEY = 'ZGV2'
    SQLALCHEMY_DATABASE_URI = 'mysql://root@localhost:3306/roomiez_testing'
    DEBUG = True
    TESTING = True
