from .development import DevelopmentConfig
from .production import ProductionConfig
from .testing import TestingConfig
from .error_codes import ErrorCode  # noqa:F401

_REQUIRED_CONFIG_KEYS = ['SECRET_KEY', 'SQLALCHEMY_DATABASE_URI']


def _get_config_object(app):
    if app.testing:
        return TestingConfig
    elif app.env == 'development':
        return DevelopmentConfig
    else:
        return ProductionConfig


def init_app(app, testConfig=None):
    if testConfig is not None:
        app.config.update(testConfig)
    else:
        app.config.from_pyfile('config.py', silent=True)

    cfgObj = _get_config_object(app)
    app.config.from_object(cfgObj())

    for key in _REQUIRED_CONFIG_KEYS:
        if app.config.get(key, None) is None:
            raise ValueError('No {} in config'.format(key))
