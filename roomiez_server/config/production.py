from .base import ConfigBase


class ProductionConfig(ConfigBase):
    SQLALCHEMY_DATABASE_URI = 'mysql://root@localhost:3306/roomiez'
    DEBUG = False
    TESTING = False
