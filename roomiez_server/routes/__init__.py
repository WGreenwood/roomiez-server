

def init_app(app):
    # Prepare json module to be able to (de)serialize datetime.datetime
    from json import JSONEncoder
    from datetime import datetime
    JSONEncoder.default = lambda self, obj: (obj.isoformat() if isinstance(obj, datetime) else None)

    from . import auth
    app.register_blueprint(auth.blueprint)

    from . import household
    household.init_routes(app)

    from . import billing
    billing.init_routes(app)
