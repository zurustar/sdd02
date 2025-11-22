from datetime import datetime, timedelta

from app import db
from app.models import Room, Schedule

from tests.test_calendar import login


def test_room_in_use_cannot_be_deleted(client, user_factory):
    admin = user_factory(username="admin", password="Password123")
    room = Room(name="Conference A", capacity=10)
    db.session.add(room)
    db.session.commit()

    start = datetime.utcnow()
    schedule = Schedule(
        title="Planning",
        start_time=start,
        end_time=start + timedelta(hours=1),
        owner=admin,
        room=room,
    )
    db.session.add(schedule)
    db.session.commit()

    login(client, "admin", "Password123")

    response = client.post(f"/rooms/{room.id}/delete", follow_redirects=True)

    assert response.status_code == 200
    assert b"Cannot delete a room that is assigned to existing schedules" in response.data
    assert db.session.get(Room, room.id) is not None


def test_create_room_success(client, user_factory):
    user_factory(username="admin", password="Password123")
    login(client, "admin", "Password123")

    response = client.post(
        "/rooms/new",
        data={"name": "Conference B", "capacity": "5", "submit": "Save"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Room created." in response.data
    assert Room.query.filter_by(name="Conference B").one().capacity == 5


def test_create_room_rejects_duplicate_name(client, user_factory):
    user_factory(username="admin", password="Password123")
    existing_room = Room(name="Conference C", capacity=8)
    db.session.add(existing_room)
    db.session.commit()

    login(client, "admin", "Password123")

    response = client.post(
        "/rooms/new",
        data={"name": "Conference C", "capacity": "10", "submit": "Save"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Room name already exists." in response.data
    assert Room.query.filter_by(name="Conference C").one().capacity == 8


def test_edit_room_prevents_name_conflict(client, user_factory):
    user_factory(username="admin", password="Password123")
    primary = Room(name="Conference D", capacity=5)
    conflict = Room(name="Conference E", capacity=7)
    db.session.add_all([primary, conflict])
    db.session.commit()

    login(client, "admin", "Password123")

    response = client.post(
        f"/rooms/{primary.id}/edit",
        data={"name": "Conference E", "capacity": "9", "submit": "Save"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Another room with this name already exists." in response.data
    db.session.refresh(primary)
    assert primary.name == "Conference D"
    assert primary.capacity == 5


def test_delete_room_without_bookings(client, user_factory):
    user_factory(username="admin", password="Password123")
    room = Room(name="Conference F", capacity=6)
    db.session.add(room)
    db.session.commit()

    login(client, "admin", "Password123")

    response = client.post(f"/rooms/{room.id}/delete", follow_redirects=True)

    assert response.status_code == 200
    assert b"Room deleted." in response.data
    assert db.session.get(Room, room.id) is None
