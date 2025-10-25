# Tasks

- [x] Set up the Flask project structure and initial files. (See `app/__init__.py`, `run.py`.)
- [x] Initialize the database. (Database models and CLI in `app/models.py`, `app/cli.py`.)
- [x] Set up testing framework (pytest).
    - [x] Install testing libraries (pytest, pytest-flask).
    - [x] Create a basic test file (e.g., `tests/test_basic.py`).
    - [x] Run pytest to verify setup. (`pytest`)
- [x] Implement user registration and login functionality. (`app/routes.py`, forms in `app/forms.py`.)
- [x] Write tests for authentication (registration, login, logout). (`tests/test_auth.py`)
- [x] Create a basic layout with navigation. (`app/templates/`)
- [x] Implement the main calendar view for schedules. (`app/routes.py::calendar`, template `app/templates/calendar.html`.)
- [x] Implement schedule creation and editing functionality. (`app/routes.py::create_schedule`, `app/routes.py::edit_schedule`)
- [x] Write tests for schedule CRUD operations. (`tests/test_calendar.py`)
- [x] Implement schedule deletion functionality. (`app/routes.py::delete_schedule`)
- [x] Implement meeting room management (CRUD). (`app/routes.py` room endpoints)
- [x] Write tests for room management. (`tests/test_rooms.py`)
- [x] Implement team schedule sharing features. (`Schedule.participants` in `app/models.py`, schedule forms/routes.)
- [x] Write tests for sharing features. (`tests/test_calendar.py::test_shared_schedule_visible_to_participant`)
