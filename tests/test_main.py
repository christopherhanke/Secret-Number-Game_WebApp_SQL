import os
import pytest
from main import app, db
from models import User


@pytest.fixture
def client():
    app.config["TESTING"] = True
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    client = app.test_client()

    cleanup()

    db.create_all()

    yield client


@pytest.fixture
def user():
    user = User(
        name="John",
        email="user@example.de",
        session_token="token",
        secret_number=10,
        deleted=False
    )

    db.add(user)
    db.commit()

    return user


@pytest.fixture
def client_authenticated(client, user):
    client.set_cookie("localhost", "session_token", user.session_token)

    return client


def cleanup():
    # clean up the database by deleting it
    db.drop_all()


def test_index_not_logged_in(client):
    response = client.get("/")
    assert b"Enter your name" in response.data


def test_login(client):
    response = client.post(
        "/",
        data={"user-name": "Test user", "user-email": "test@example.de", "user-password": "password123"})

    assert b"Enter a number" in response.data


def test_logged_in_index(client_authenticated):
    response = client_authenticated.get("/game")
    assert b"Enter a number" in response.data


def test_profile(client_authenticated):
    response = client_authenticated.get("/profile")
    assert b"user@example.de" in response.data


def test_guess_lower_number(client_authenticated):
    response = client_authenticated.post("/game", data={"guess": 8})
    assert b"below the secret" in response.data


def test_guess_higher_number(client_authenticated):
    response = client_authenticated.post("/game", data={"guess": 12})
    assert b"above the secret" in response.data


def test_guess_correct(client_authenticated):
    response = client_authenticated.post("/game", data={"guess": 10})
    assert b"Hooray" in response.data
