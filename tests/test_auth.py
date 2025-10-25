from app.models import User


def test_registration_creates_user_and_redirects_to_login(client):
    response = client.post(
        "/register",
        data={
            "username": "newuser",
            "password": "Password123",
            "password2": "Password123",
            "submit": "Register",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Registration successful" in response.data
    assert User.query.filter_by(username="newuser").one().check_password("Password123")


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


def test_login_succeeds_with_valid_credentials(client, user_factory):
    user_factory(username="validuser", password="Password123")

    response = client.post(
        "/login",
        data={
            "username": "validuser",
            "password": "Password123",
            "submit": "Log In",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Welcome back!" in response.data
    assert b"Team Calendar" in response.data


def test_logout_clears_session(client, user_factory):
    user_factory(username="logout-user", password="Password123")

    client.post(
        "/login",
        data={
            "username": "logout-user",
            "password": "Password123",
            "submit": "Log In",
        },
        follow_redirects=True,
    )

    response = client.get("/logout", follow_redirects=True)

    assert response.status_code == 200
    assert b"You have been logged out." in response.data
