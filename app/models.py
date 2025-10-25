from datetime import datetime

from app import db, login
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

schedule_participants = db.Table(
    'schedule_participants',
    db.Column('schedule_id', db.Integer, db.ForeignKey('schedule.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    schedules = db.relationship('Schedule', back_populates='owner', lazy='dynamic')
    shared_schedules = db.relationship(
        'Schedule',
        secondary=schedule_participants,
        back_populates='participants',
        lazy='dynamic'
    )

    def set_password(self, password):
        """Generate a password hash using a broadly supported algorithm."""
        # Some Python builds omit ``hashlib.scrypt`` which Werkzeug may default to
        # when selecting a hashing algorithm. Explicitly request PBKDF2 to stay
        # compatible across environments that lack ``scrypt`` support.
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    start_time = db.Column(db.DateTime, index=True, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(140))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', back_populates='schedules')
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    room = db.relationship('Room', back_populates='schedules')
    participants = db.relationship(
        'User',
        secondary=schedule_participants,
        back_populates='shared_schedules'
    )

    def is_owned_by(self, user):
        return self.owner_id == user.id

    def __repr__(self):
        return f'<Schedule {self.title}>'


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    schedules = db.relationship('Schedule', back_populates='room', lazy='dynamic')

    def __repr__(self):
        return f'<Room {self.name}>'
