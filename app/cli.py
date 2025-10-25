import click
from flask.cli import with_appcontext

from app import db


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Create all database tables."""
    db.create_all()
    click.echo('Database initialized.')


def register_commands(app):
    app.cli.add_command(init_db_command)
