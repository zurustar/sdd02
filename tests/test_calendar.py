from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path

from app import db
from app.models import Room, Schedule
from flask import template_rendered


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):  # pragma: no cover - signal hook
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


def login(client, username, password):
    return client.post(
        "/login",
        data={"username": username, "password": password, "submit": "Log In"},
        follow_redirects=True,
    )


def test_shared_schedule_visible_to_participant(client, user_factory):
    owner = user_factory(username="owner", password="Password123")
    participant = user_factory(username="participant", password="Password123")

    start = datetime.utcnow().replace(hour=12, minute=0, second=0, microsecond=0)
    schedule = Schedule(
        title="Team Sync",
        start_time=start,
        end_time=start + timedelta(hours=1),
        owner=owner,
    )
    schedule.participants.append(participant)
    db.session.add(schedule)
    db.session.commit()

    login_response = login(client, "participant", "Password123")
    assert b"Welcome back!" in login_response.data

    calendar_response = client.get("/calendar")
    assert calendar_response.status_code == 200
    assert b"Team Sync" in calendar_response.data


def test_calendar_view_provides_weekly_planner_context(app, client, user_factory):
    owner = user_factory(username="owner", password="Password123")
    login(client, "owner", "Password123")

    now = datetime.utcnow()
    week_start = now - timedelta(days=now.weekday())
    reference_day = week_start + timedelta(days=2)
    event_start = reference_day.replace(hour=9, minute=0, second=0, microsecond=0)
    event_end = event_start + timedelta(hours=2)

    schedule = Schedule(
        title="Strategy Session",
        start_time=event_start,
        end_time=event_end,
        owner=owner,
        location="War Room",
    )
    db.session.add(schedule)
    db.session.commit()

    with captured_templates(app) as templates:
        response = client.get("/calendar")

    assert response.status_code == 200
    assert templates, "Calendar view should render a template"
    template, context = templates[0]
    assert template.name == "calendar.html"

    planner = context.get("planner")
    assert planner is not None, "Planner context should be provided"

    assert planner["week_start"].date() == week_start.date()
    assert len(planner["days"]) == 7
    assert planner["hours"][0]["label"] == "06:00"
    assert planner["hours"][-1]["label"] == "22:00"

    wednesday = planner["days"][2]
    assert wednesday["date"].date() == reference_day.date()
    assert wednesday["events"], "Expected events for Wednesday"
    event = wednesday["events"][0]
    assert event["title"] == "Strategy Session"
    assert event["start_minutes"] == 180
    assert event["duration_minutes"] == 120
    assert event["column_span"] >= 1


def test_calendar_template_renders_grid_structure(client, user_factory):
    owner = user_factory(username="owner", password="Password123")
    login(client, "owner", "Password123")

    response = client.get("/calendar")

    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "planner-grid" in html
    assert "role=\"grid\"" in html
    assert html.count("planner-grid__cell") >= 7 * 5  # at least five rows across seven days


def test_calendar_template_includes_accessibility_attributes(client, user_factory):
    owner = user_factory(username="owner", password="Password123")
    login(client, "owner", "Password123")

    start = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
    schedule = Schedule(
        title="Design Review",
        start_time=start,
        end_time=start + timedelta(hours=1),
        owner=owner,
    )
    db.session.add(schedule)
    db.session.commit()

    response = client.get("/calendar")

    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "aria-label=\"Weekly planner" in html
    assert "tabindex=\"0\"" in html
    assert "planner-event" in html


def test_planner_styles_include_responsive_rules():
    css_path = Path("app/static/css/planner.css")
    assert css_path.exists(), "Planner stylesheet should exist"
    css_text = css_path.read_text(encoding="utf-8")
    assert "@media" in css_text
    assert "max-width" in css_text


def test_non_owner_cannot_access_edit_form(client, user_factory):
    owner = user_factory(username="schedule-owner", password="Password123")
    intruder = user_factory(username="intruder", password="Password123")

    start = datetime.utcnow()
    schedule = Schedule(
        title="Private Meeting",
        start_time=start,
        end_time=start + timedelta(hours=1),
        owner=owner,
    )
    db.session.add(schedule)
    db.session.commit()

    login(client, "intruder", "Password123")

    response = client.get(f"/schedules/{schedule.id}/edit")
    assert response.status_code == 403


def test_schedule_creation_rejects_end_time_before_start(client, user_factory):
    owner = user_factory(username="owner", password="Password123")
    login(client, "owner", "Password123")

    start = datetime.utcnow().replace(microsecond=0, second=0)
    response = client.post(
        "/schedules/new",
        data={
            "title": "Invalid",
            "start_time": start.strftime("%Y-%m-%dT%H:%M"),
            "end_time": (start - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M"),
            "location": "", 
            "room": "0",
            "participants": [],
            "submit": "Save",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"End time must be after the start time." in response.data
    assert Schedule.query.count() == 0


def test_schedule_creation_assigns_room_and_participants(client, user_factory):
    owner = user_factory(username="owner", password="Password123")
    teammate = user_factory(username="teammate", password="Password123")
    room = Room(name="Conference B", capacity=8)
    db.session.add(room)
    db.session.commit()

    login(client, "owner", "Password123")

    start = datetime.utcnow().replace(microsecond=0, second=0)
    response = client.post(
        "/schedules/new",
        data={
            "title": "Planning",
            "start_time": start.strftime("%Y-%m-%dT%H:%M"),
            "end_time": (start + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M"),
            "location": "Main Room",
            "room": str(room.id),
            "participants": [str(teammate.id)],
            "submit": "Save",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert response.request.path == "/calendar"

    schedule = Schedule.query.filter_by(title="Planning").one()
    assert schedule.room_id == room.id
    participant_usernames = {user.username for user in schedule.participants}
    assert participant_usernames == {"teammate"}
    assert schedule.is_owned_by(owner)


def test_owner_can_update_schedule_details(client, user_factory):
    owner = user_factory(username="owner", password="Password123")
    teammate = user_factory(username="teammate", password="Password123")
    other = user_factory(username="other", password="Password123")
    room_initial = Room(name="Conference C", capacity=4)
    room_updated = Room(name="Conference D", capacity=6)
    db.session.add_all([room_initial, room_updated])
    db.session.commit()

    start = datetime.utcnow()
    schedule = Schedule(
        title="Weekly Sync",
        start_time=start,
        end_time=start + timedelta(hours=1),
        owner=owner,
        room=room_initial,
    )
    schedule.participants.append(teammate)
    db.session.add(schedule)
    db.session.commit()

    login(client, "owner", "Password123")

    response = client.post(
        f"/schedules/{schedule.id}/edit",
        data={
            "title": "Updated Sync",
            "start_time": (start + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
            "end_time": (start + timedelta(days=1, hours=2)).strftime("%Y-%m-%dT%H:%M"),
            "location": "New Location",
            "room": str(room_updated.id),
            "participants": [str(other.id)],
            "submit": "Save",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert response.request.path == "/calendar"

    db.session.refresh(schedule)
    assert schedule.title == "Updated Sync"
    assert schedule.room_id == room_updated.id
    assert schedule.location == "New Location"
    participant_usernames = {user.username for user in schedule.participants}
    assert participant_usernames == {"other"}


def test_owner_can_delete_schedule(client, user_factory):
    owner = user_factory(username="owner", password="Password123")
    start = datetime.utcnow()
    schedule = Schedule(
        title="Temporary",
        start_time=start,
        end_time=start + timedelta(hours=1),
        owner=owner,
    )
    db.session.add(schedule)
    db.session.commit()

    login(client, "owner", "Password123")

    response = client.post(f"/schedules/{schedule.id}/delete", follow_redirects=True)

    assert response.status_code == 200
    assert b"Schedule deleted." in response.data
    assert Schedule.query.get(schedule.id) is None


def test_non_owner_cannot_delete_schedule(client, user_factory):
    owner = user_factory(username="owner", password="Password123")
    intruder = user_factory(username="intruder", password="Password123")
    start = datetime.utcnow()
    schedule = Schedule(
        title="Protected",
        start_time=start,
        end_time=start + timedelta(hours=1),
        owner=owner,
    )
    db.session.add(schedule)
    db.session.commit()

    login(client, "intruder", "Password123")

    response = client.post(f"/schedules/{schedule.id}/delete")

    assert response.status_code == 403
    assert Schedule.query.get(schedule.id) is not None
