

def init_routes(app):
    from . import base
    app.register_blueprint(base.blueprint)

    from . import invitations
    app.register_blueprint(invitations.blueprint)
