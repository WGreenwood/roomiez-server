
def init_routes(app):
    from . import bills
    app.register_blueprint(bills.blueprint)

    from . import cycles
    app.register_blueprint(cycles.blueprint)

    from . import payments
    app.register_blueprint(payments.cycle_payments_blueprint)
    app.register_blueprint(payments.bill_payments_blueprint)
