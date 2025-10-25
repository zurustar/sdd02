from datetime import datetime, timedelta

from app import db
from app.models import Room, Schedule


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
