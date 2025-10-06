# Project Setup Guide

This guide will help you set up the Norimberga development environment from scratch.

## Prerequisites

- Python 3.13 or higher
- Node.js and npm (for TailwindCSS)
- Git

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/GitRon/norimberga.git
cd norimberga
```

### 2. Install Dependencies

This project uses `uv` for Python dependency management:

```bash
# Install dependencies (development and production)
uv sync --group dev
```

If you don't have `uv` installed, you can install it first:
```bash
pip install -U uv
```

### 3. Database Setup

The project uses SQLite for development, which requires no separate installation. The database file will be created automatically.

#### Create Database and Run Migrations

```bash
python manage.py migrate
```

This creates the SQLite database file (typically `db.sqlite3`) and applies all migrations to set up the database schema.

#### Load Initial Fixtures

The project includes fixture data that should be loaded to set up the game properly:

```bash
# Load all fixtures in order
python manage.py loaddata apps/city/fixtures/terrains.json
python manage.py loaddata apps/city/fixtures/building_types.json
python manage.py loaddata apps/city/fixtures/buildings.json
python manage.py loaddata apps/milestone/fixtures/milestones.json
python manage.py loaddata apps/milestone/fixtures/milestone_conditions.json
```

All fixtures are required for the game to function correctly with its initial data.

### 4. Create Superuser Account

To access the Django admin interface, create a superuser account:

```bash
python manage.py createsuperuser
```

You'll be prompted to enter:
- Username
- Email address (optional)
- Password

Once created, you can access the admin interface at `http://localhost:8000/admin/` after starting the server.

### 5. Build Frontend Assets

Install Node.js dependencies and build TailwindCSS:

```bash
# Install Node.js dependencies
npm install

# Build CSS (one-time build)
npx tailwindcss -i ./static/css/input.css -o ./static/css/dist/output.css
```

## Running the Development Server

### Start the Backend Server

```bash
python manage.py runserver
```

The server will be available at `http://localhost:8000/`

### Watch TailwindCSS Changes (Development)

In a separate terminal, run the TailwindCSS watcher to automatically rebuild CSS when you make changes:

```bash
npx tailwindcss -i ./static/css/input.css -o ./static/css/dist/output.css --watch
```

## Database Information

### SQLite Usage

- **Database file location**: `db.sqlite3` (in project root)
- **No separate server needed**: SQLite is file-based and built into Python
- **Viewing the database**: Use tools like:
  - [DB Browser for SQLite](https://sqlitebrowser.org/) (GUI)
  - `sqlite3` command-line tool
  - Django admin interface at `/admin/`

### Common Database Commands

```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (WARNING: destroys all data)
# Delete db.sqlite3 and run migrate again
rm db.sqlite3
python manage.py migrate
python manage.py loaddata apps/city/fixtures/terrains.json
python manage.py loaddata apps/city/fixtures/building_types.json
python manage.py loaddata apps/city/fixtures/buildings.json
python manage.py loaddata apps/milestone/fixtures/milestones.json
python manage.py loaddata apps/milestone/fixtures/milestone_conditions.json
python manage.py createsuperuser
```

## Verifying Your Setup

1. **Check server is running**: Visit `http://localhost:8000/`
2. **Check admin access**: Visit `http://localhost:8000/admin/` and log in with your superuser credentials
3. **Run tests**: Ensure everything is working correctly

```bash
pytest
```

## Next Steps

- Read the main [CLAUDE.md](../../CLAUDE.md) for development commands and workflow
- Review architecture patterns in `docs/patterns/`
- Check the test coverage: `pytest --cov=apps --cov-report=html` and open `htmlcov/index.html`

## Troubleshooting

### Database locked errors
SQLite can have concurrency issues. Make sure only one process is accessing the database at a time.

### Missing tables errors
Run migrations: `python manage.py migrate`

### Static files not loading
Make sure you've built the CSS with TailwindCSS and that `DEBUG = True` in settings (for development).

### Admin interface styling broken
Ensure you've run `python manage.py collectstatic` if needed, or check that the TailwindCSS build completed successfully.
