import pytest

import testdata
import flask_migrate
from roomiez_server import create_app, DB
from roomiez_server.helpers import security
from roomiez_server.models import User, Bill, BillPayment, BillType  # noqa: F401


def _table_names():
    return [tbl.name for tbl in DB.metadata.sorted_tables] + ['alembic_version']


def downgrade():
    DB.session.execute('SET FOREIGN_KEY_CHECKS = 0;')
    DB.session.commit()
    for tblName in _table_names():
        DB.engine.execute('DROP TABLE IF EXISTS `{}`;'.format(tblName))
    DB.session.execute('SET FOREIGN_KEY_CHECKS = 1;')
    DB.session.commit()


def get_jwt(userIdx, app):
    userData = testdata.EXISTING_USERS[userIdx]
    email, password = userData['email'], userData['password']
    user, jwt = None, None
    with app.app_context():
        user, jwt = security.do_login(email, password)
    assert user is not None
    assert jwt is not None
    return jwt


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True
    })

    with app.app_context():
        downgrade()
        flask_migrate.upgrade()
        testdata.insert_all(DB)

    yield app

    with app.app_context():
        downgrade()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def userJwt(app):
    return get_jwt(1, app)


@pytest.fixture
def adminJwt(app):
    return get_jwt(0, app)


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
