from datetime import datetime, timedelta

from app import db
from app.models import Schedule


def login(client, username, password):
    return client.post(
        "/login",
        data={"username": username, "password": password, "submit": "Log In"},
        follow_redirects=True,
    )


def test_shared_schedule_visible_to_participant(client, user_factory):
    owner = user_factory(username="owner", password="Password123")
    participant = user_factory(username="participant", password="Password123")

    start = datetime.utcnow()
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
