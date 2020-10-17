
def init_app(app):
    from .new_secret import new_secret
    app.cli.add_command(new_secret)

    from .destroy_db import destroy_db
    app.cli.add_command(destroy_db)
