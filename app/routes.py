from datetime import datetime, timedelta

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import or_

from app import db
from app.forms import LoginForm, RegistrationForm, RoomForm, ScheduleForm
from app.models import Room, Schedule, User

bp = Blueprint('main', __name__)


def _populate_schedule_form_choices(form, *, current_user):
    form.room.choices = [(0, 'No room assigned')] + [
        (room.id, room.name) for room in Room.query.order_by(Room.name).all()
    ]
    form.participants.choices = [
        (user.id, user.username)
        for user in User.query.order_by(User.username).all()
        if user.id != current_user.id
    ]


def _build_planner_hours(*, start_hour, end_hour, interval_minutes):
    step = max(interval_minutes, 15)  # guard against zero
    hours = []
    current = start_hour
    while current <= end_hour:
        label = f"{current:02d}:00"
        hours.append({"hour": current, "label": label})
        current += step // 60
        if step % 60 != 0:
            break  # interval other than 60 minutes currently unsupported
    if not hours:
        raise ValueError("Planner hours configuration produced no slots")
    return hours


def _normalize_minutes(delta):
    return int(delta.total_seconds() // 60)


def _assign_event_columns(events):
    if not events:
        return

    events.sort(key=lambda item: (item["start_minutes"], item["end_minutes"]))
    active = []
    clusters = []

    for event in events:
        active = [e for e in active if e["end_minutes"] > event["start_minutes"]]
        if active:
            cluster = active[0]["cluster"]
        else:
            cluster = {"events": []}
            clusters.append(cluster)
        used_columns = {e["column"] for e in active}
        column = 0
        while column in used_columns:
            column += 1
        event["column"] = column
        event["cluster"] = cluster
        cluster["events"].append(event)
        active.append(event)

    for cluster in clusters:
        columns = {event["column"] for event in cluster["events"]}
        width = max(columns) + 1 if columns else 1
        for event in cluster["events"]:
            event["column_span"] = width
            event["column_offset"] = event["column"]


def _build_planner(schedules, *, week_start, viewer):
    config = current_app.config
    start_hour = config.get("PLANNER_START_HOUR", 6)
    end_hour = config.get("PLANNER_END_HOUR", 22)
    interval_minutes = config.get("PLANNER_INTERVAL_MINUTES", 60)

    hours = _build_planner_hours(
        start_hour=start_hour,
        end_hour=end_hour,
        interval_minutes=interval_minutes,
    )

    days = []
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    display_span = end_hour - start_hour

    for day_index in range(7):
        day_start = week_start + timedelta(days=day_index)
        day_end = day_start + timedelta(days=1)
        display_start = day_start + timedelta(hours=start_hour)
        display_end = day_start + timedelta(hours=end_hour)
        day_label = day_start.strftime("%A %d %b")
        events = []

        for schedule in schedules:
            if schedule.end_time <= day_start or schedule.start_time >= day_end:
                continue

            event_start = max(schedule.start_time, display_start)
            event_end = min(schedule.end_time, display_end)
            if event_end <= event_start:
                continue

            start_minutes = _normalize_minutes(event_start - display_start)
            end_minutes = _normalize_minutes(event_end - display_start)
            duration_minutes = max(end_minutes - start_minutes, 15)
            owner_name = schedule.owner.username if schedule.owner else ""
            room_name = schedule.room.name if schedule.room else None
            aria_label_parts = [
                schedule.title,
                f"on {day_start.strftime('%A %d %B %Y')}",
                f"from {event_start.strftime('%H:%M')} to {event_end.strftime('%H:%M')}",
            ]
            if schedule.location:
                aria_label_parts.append(f"at {schedule.location}")
            events.append(
                {
                    "id": schedule.id,
                    "title": schedule.title,
                    "location": schedule.location,
                    "room": room_name,
                    "start_minutes": start_minutes,
                    "end_minutes": end_minutes,
                    "duration_minutes": duration_minutes,
                    "start_time": schedule.start_time,
                    "end_time": schedule.end_time,
                    "display_start": event_start,
                    "display_end": event_end,
                    "owner": owner_name,
                    "column": 0,
                    "column_span": 1,
                    "column_offset": 0,
                    "is_owner": schedule.is_owned_by(viewer),
                    "participants": [user.username for user in schedule.participants],
                    "aria_label": ", ".join(aria_label_parts),
                }
            )

        _assign_event_columns(events)

        days.append(
            {
                "date": day_start,
                "label": day_label,
                "cell_labels": [
                    f"{day_start.strftime('%A %d %B %Y')} at {hour['label']}" for hour in hours
                ],
                "events": events,
                "display_start": display_start,
                "display_hours": display_span,
            }
        )

    return {
        "week_start": week_start,
        "hours": hours,
        "days": days,
        "start_hour": start_hour,
        "end_hour": end_hour,
    }


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.calendar'))
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
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.calendar'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.', 'danger')
            return render_template('login.html', title='Log In', form=form)
        login_user(user)
        flash('Welcome back!', 'success')
        return redirect(url_for('main.calendar'))
    return render_template('login.html', title='Log In', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@bp.route('/calendar')
@login_required
def calendar():
    reference = datetime.utcnow()
    week_start = reference - timedelta(days=reference.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)

    schedules = Schedule.query.filter(
        or_(
            Schedule.owner_id == current_user.id,
            Schedule.participants.any(id=current_user.id)
        ),
        Schedule.end_time > week_start,
        Schedule.start_time < week_end,
    ).order_by(Schedule.start_time.asc()).all()

    planner = _build_planner(schedules, week_start=week_start, viewer=current_user)
    return render_template('calendar.html', title='Calendar', schedules=schedules, planner=planner)


@bp.route('/schedules/new', methods=['GET', 'POST'])
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
        db.session.add(schedule)
        if form.room.data:
            schedule.room = db.session.get(Room, form.room.data)
        participant_ids = [pid for pid in form.participants.data if pid != current_user.id]
        if participant_ids:
            schedule.participants = User.query.filter(User.id.in_(participant_ids)).all()
        db.session.commit()
        flash('Schedule created.', 'success')
        return redirect(url_for('main.calendar'))
    return render_template('schedule_form.html', title='New Schedule', form=form)


@bp.route('/schedules/<int:schedule_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_schedule(schedule_id):
    schedule = db.session.get(Schedule, schedule_id)
    if schedule is None:
        abort(404)
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
        schedule.room = db.session.get(Room, form.room.data) if form.room.data else None
        participant_ids = [pid for pid in form.participants.data if pid != current_user.id]
        schedule.participants = User.query.filter(User.id.in_(participant_ids)).all() if participant_ids else []
        db.session.commit()
        flash('Schedule updated.', 'success')
        return redirect(url_for('main.calendar'))
    return render_template('schedule_form.html', title='Edit Schedule', form=form, schedule=schedule)


@bp.route('/schedules/<int:schedule_id>/delete', methods=['POST'])
@login_required
def delete_schedule(schedule_id):
    schedule = db.session.get(Schedule, schedule_id)
    if schedule is None:
        abort(404)
    if not schedule.is_owned_by(current_user):
        abort(403)
    db.session.delete(schedule)
    db.session.commit()
    flash('Schedule deleted.', 'info')
    return redirect(url_for('main.calendar'))


@bp.route('/rooms')
@login_required
def list_rooms():
    rooms = Room.query.order_by(Room.name).all()
    return render_template('room_list.html', title='Meeting Rooms', rooms=rooms)


@bp.route('/rooms/new', methods=['GET', 'POST'])
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
        return redirect(url_for('main.list_rooms'))
    return render_template('room_form.html', title='New Room', form=form)


@bp.route('/rooms/<int:room_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_room(room_id):
    room = db.session.get(Room, room_id)
    if room is None:
        abort(404)
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
        return redirect(url_for('main.list_rooms'))
    return render_template('room_form.html', title='Edit Room', form=form, room=room)


@bp.route('/rooms/<int:room_id>/delete', methods=['POST'])
@login_required
def delete_room(room_id):
    room = db.session.get(Room, room_id)
    if room is None:
        abort(404)
    if room.schedules.count():
        flash('Cannot delete a room that is assigned to existing schedules.', 'warning')
        return redirect(url_for('main.list_rooms'))
    db.session.delete(room)
    db.session.commit()
    flash('Room deleted.', 'info')
    return redirect(url_for('main.list_rooms'))
