import click
from flask.cli import with_appcontext

from roomiez_server import DB


def _table_names():
    return [tbl.name for tbl in DB.metadata.sorted_tables] + ['alembic_version']


def downgrade():
    DB.session.execute('SET FOREIGN_KEY_CHECKS = 0;')
    DB.session.commit()
    for tblName in _table_names():
        DB.engine.execute('DROP TABLE IF EXISTS `{}`;'.format(tblName))
    DB.session.execute('SET FOREIGN_KEY_CHECKS = 1;')
    DB.session.commit()


@click.command('destroydb', help='Deletes all tables associated with models in the database')
@click.option('-f', is_flag=True, default=False,
              help='Force the operation. This will invalidate all existing sessions')
@with_appcontext
def destroy_db(f):
    if not f:
        prompt = click.prompt('This will invalidate all existing sessions. \nWould you like to continue? (y/n)')
        if not prompt or prompt.lower() != 'y':
            click.echo('Aborting...')
            return

    downgrade()
    click.echo(f'Tables deleted: {_table_names()}')
