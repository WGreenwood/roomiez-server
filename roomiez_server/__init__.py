import os
import sys
from contextlib import suppress

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from roomiez_server import cli, config, routes

DB = SQLAlchemy()
migrate = Migrate()

from roomiez_server import models  # noqa: F401


def create_app(testConfig=None) -> Flask:
    sys.dont_write_bytecode = True
    app = Flask(__name__, instance_relative_config=True)

    # with suppress(OSError):
    # os.makedirs(app.instance_path)

    config.init_app(app, testConfig)

    DB.init_app(app)
    migrate.init_app(app, db=DB)

    cli.init_app(app)

    routes.init_app(app)

    return app
