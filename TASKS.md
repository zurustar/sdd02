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
- [x] Document the weekly planner redesign requirements. (`README.md`, `docs/`)

## Upcoming Work

- [x] Implement the weekly planner template so days render horizontally and hours vertically. (Update `app/templates/calendar.html`, introduce partials in `app/templates/partials/`.)
    - [x] Restructure the calendar view HTML to generate a seven-day grid with labeled hour rows sourced from configuration.
    - [x] Add CSS modules under `app/static/css/` to position schedule blocks within the grid and visually distinguish overlaps.
- [x] Expose planner-friendly schedule data from the calendar route. (Refine `app/routes.py::calendar` helpers to group events per day/hour block.)
- [x] Provide keyboard navigation and ARIA labelling for the planner. (Enhance template semantics and add guidance in `docs/weekly_planner_design.md`.)
- [x] Add responsive tweaks for tablet and mobile breakpoints. (Extend the planner stylesheet with media queries.)
- [x] Expand automated coverage for the new layout. (Add view tests in `tests/test_calendar.py` and adjust snapshot data as needed.)
