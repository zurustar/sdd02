import click

from app import app, db


@app.cli.command('init-db')
def init_db_command():
    """Create all database tables."""
    db.create_all()
    click.echo('Database initialized.')
