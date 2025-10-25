from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import or_

from app import app, db
from app.forms import LoginForm, RegistrationForm, RoomForm, ScheduleForm
from app.models import Room, Schedule, User


def _populate_schedule_form_choices(form, *, current_user):
    form.room.choices = [(0, 'No room assigned')] + [
        (room.id, room.name) for room in Room.query.order_by(Room.name).all()
    ]
    form.participants.choices = [
        (user.id, user.username)
        for user in User.query.order_by(User.username).all()
        if user.id != current_user.id
    ]


from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('calendar'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken. Please choose another one.', 'danger')
            return render_template('register.html', title='Register', form=form)
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('calendar'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.', 'danger')
            return render_template('login.html', title='Log In', form=form)
        login_user(user)
        flash('Welcome back!', 'success')
        return redirect(url_for('calendar'))
    return render_template('login.html', title='Log In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/calendar')
@login_required
def calendar():
    schedules = Schedule.query.filter(
        or_(
            Schedule.owner_id == current_user.id,
            Schedule.participants.any(id=current_user.id)
        )
    ).order_by(Schedule.start_time.asc()).all()
    return render_template('calendar.html', title='Calendar', schedules=schedules)


@app.route('/schedules/new', methods=['GET', 'POST'])
@login_required
def create_schedule():
    form = ScheduleForm()
    _populate_schedule_form_choices(form, current_user=current_user)
    if form.validate_on_submit():
        if form.end_time.data <= form.start_time.data:
            form.end_time.errors.append('End time must be after the start time.')
            return render_template('schedule_form.html', title='New Schedule', form=form)
        schedule = Schedule(
            title=form.title.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            location=form.location.data,
            owner=current_user
        )
        if form.room.data:
            room = Room.query.get(form.room.data)
            schedule.room = room
        participant_ids = [pid for pid in form.participants.data if pid != current_user.id]
        if participant_ids:
            schedule.participants = User.query.filter(User.id.in_(participant_ids)).all()
        db.session.add(schedule)
        db.session.commit()
        flash('Schedule created.', 'success')
        return redirect(url_for('calendar'))
    return render_template('schedule_form.html', title='New Schedule', form=form)


@app.route('/schedules/<int:schedule_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    if not schedule.is_owned_by(current_user):
        abort(403)
    form = ScheduleForm(obj=schedule)
    _populate_schedule_form_choices(form, current_user=current_user)
    if request.method == 'GET':
        form.room.data = schedule.room_id or 0
        form.participants.data = [user.id for user in schedule.participants]
    if form.validate_on_submit():
        if form.end_time.data <= form.start_time.data:
            form.end_time.errors.append('End time must be after the start time.')
            return render_template('schedule_form.html', title='Edit Schedule', form=form, schedule=schedule)
        schedule.title = form.title.data
        schedule.start_time = form.start_time.data
        schedule.end_time = form.end_time.data
        schedule.location = form.location.data
        schedule.room = Room.query.get(form.room.data) if form.room.data else None
        participant_ids = [pid for pid in form.participants.data if pid != current_user.id]
        schedule.participants = User.query.filter(User.id.in_(participant_ids)).all() if participant_ids else []
        db.session.commit()
        flash('Schedule updated.', 'success')
        return redirect(url_for('calendar'))
    return render_template('schedule_form.html', title='Edit Schedule', form=form, schedule=schedule)


@app.route('/schedules/<int:schedule_id>/delete', methods=['POST'])
@login_required
def delete_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    if not schedule.is_owned_by(current_user):
        abort(403)
    db.session.delete(schedule)
    db.session.commit()
    flash('Schedule deleted.', 'info')
    return redirect(url_for('calendar'))


@app.route('/rooms')
@login_required
def list_rooms():
    rooms = Room.query.order_by(Room.name).all()
    return render_template('room_list.html', title='Meeting Rooms', rooms=rooms)


@app.route('/rooms/new', methods=['GET', 'POST'])
@login_required
def create_room():
    form = RoomForm()
    if form.validate_on_submit():
        if Room.query.filter_by(name=form.name.data).first():
            flash('Room name already exists.', 'danger')
            return render_template('room_form.html', title='New Room', form=form)
        room = Room(name=form.name.data, capacity=form.capacity.data)
        db.session.add(room)
        db.session.commit()
        flash('Room created.', 'success')
        return redirect(url_for('list_rooms'))
    return render_template('room_form.html', title='New Room', form=form)


@app.route('/rooms/<int:room_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_room(room_id):
    room = Room.query.get_or_404(room_id)
    form = RoomForm(obj=room)
    if form.validate_on_submit():
        existing_room = Room.query.filter(Room.name == form.name.data, Room.id != room.id).first()
        if existing_room:
            flash('Another room with this name already exists.', 'danger')
            return render_template('room_form.html', title='Edit Room', form=form, room=room)
        room.name = form.name.data
        room.capacity = form.capacity.data
        db.session.commit()
        flash('Room updated.', 'success')
        return redirect(url_for('list_rooms'))
    return render_template('room_form.html', title='Edit Room', form=form, room=room)


@app.route('/rooms/<int:room_id>/delete', methods=['POST'])
@login_required
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    if room.schedules.count():
        flash('Cannot delete a room that is assigned to existing schedules.', 'warning')
        return redirect(url_for('list_rooms'))
    db.session.delete(room)
    db.session.commit()
    flash('Room deleted.', 'info')
    return redirect(url_for('list_rooms'))
