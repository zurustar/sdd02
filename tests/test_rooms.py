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
    assert Room.query.get(room.id) is not None
