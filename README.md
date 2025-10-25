# Team Scheduler

Team Scheduler is a Flask web application that helps small teams plan meetings, reserve rooms, and share schedules. Users can sign up, log in, and collaborate by sharing events with teammates and coordinating the use of meeting rooms.

## Features

- User registration, login, and logout flows to manage personal accounts.
- A calendar view that lists schedules a user owns or that have been shared with them.
- Creation, editing, and deletion of schedules with location details, room assignments, and team participants.
- Meeting room management with CRUD tools and safeguards against deleting rooms that are in use.
- Flash messaging and navigation that highlight key actions as you move through the app.

## Requirements

- Python 3.10 or later.
- The Python packages listed in `requirements.txt`.
- (Optional) A `SECRET_KEY` environment variable for production deployments. If it is not provided, a default value is used.

## Getting Started

1. **Clone the repository and move into the project directory.**
   ```bash
   git clone <repository-url>
   cd sdd02
   ```
2. **Create and activate a virtual environment (recommended).**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies.**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set environment variables for Flask.**
   ```bash
   export FLASK_APP=run.py
   export FLASK_ENV=development  # optional, enables debug mode
   export SECRET_KEY="change-me"  # optional, overrides the default key
   ```
5. **Initialize the database.**
   ```bash
   flask init-db
   ```
6. **Run the development server.**
   ```bash
   flask run
   ```
7. **Visit the app.**
   Open [http://localhost:5000](http://localhost:5000) in your browser.

The application uses a SQLite database stored at `app.db` by default. To use another database, set the `DATABASE_URL` environment variable before launching Flask.

## Usage

1. **Register and log in.** Create a new account, or log in if you already have one. Logged-in users can always return to the calendar from the navigation bar.
2. **Manage schedules.** Use the "Create Schedule" button from the calendar to add events. Each event requires a title, start and end time, and can include a location, room, and shared participants. You can edit or delete schedules you own directly from the calendar view.
3. **Share with teammates.** When creating or editing a schedule, select additional users to share the event with. Shared events are labeled for recipients in the calendar.
4. **Coordinate meeting rooms.** Navigate to "Meeting Rooms" to add rooms with names and capacities, update existing rooms, or remove unused ones. Rooms that are assigned to schedules cannot be deleted until the schedules are updated.
5. **Sign out.** Use the "Log Out" link in the navigation bar when you are finished.

## Maintenance Notes

- Use `flask init-db` any time you need to reset your local database schema.
- Update `requirements.txt` when adding or upgrading dependencies.
- Keep this README in sync with the user-facing functionality and setup steps as the project evolves.
