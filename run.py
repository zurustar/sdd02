from app import app, db
from app.models import Room, Schedule, User


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Schedule': Schedule, 'Room': Room}
