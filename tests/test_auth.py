from app.models import User


def test_registration_rejects_duplicate_username(client, user_factory):
    user_factory(username="existing", password="Password123")

    response = client.post(
        "/register",
        data={
            "username": "existing",
            "password": "Password123",
            "password2": "Password123",
            "submit": "Register",
        },
        follow_redirects=True,
    )

    assert b"Username already taken" in response.data
    assert User.query.filter_by(username="existing").count() == 1


def test_login_rejects_invalid_credentials(client, user_factory):
    user_factory(username="validuser", password="Password123")

    response = client.post(
        "/login",
        data={
            "username": "validuser",
            "password": "WrongPassword",
            "submit": "Log In",
        },
        follow_redirects=True,
    )

    assert b"Invalid username or password" in response.data
