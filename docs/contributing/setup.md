# Project Setup Guide

This guide will help you set up the Norimberga development environment from scratch.

## Quick Start

Already familiar with Django and TailwindCSS? Here's the essentials:

```bash
# Clone and setup
git clone https://github.com/GitRon/norimberga.git
cd norimberga
uv sync --group dev

# Database and fixtures
python manage.py migrate
python manage.py loaddata terrains building_types buildings milestones milestone_conditions
python manage.py createsuperuser

# Frontend
npm install
npx tailwindcss -i ./static/css/input.css -o ./static/css/dist/output.css

# Run (in two terminals)
python manage.py runserver
npx tailwindcss -i ./static/css/input.css -o ./static/css/dist/output.css --watch
```

For detailed instructions, continue reading below.

## Prerequisites

- Python 3.13 or higher
- Node.js and npm (for TailwindCSS)
- Git

## Initial Setup (One-Time)

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
python manage.py loaddata terrains
python manage.py loaddata building_types
python manage.py loaddata buildings
python manage.py loaddata milestones
python manage.py loaddata milestone_conditions
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

Install Node.js dependencies and build TailwindCSS with DaisyUI:

```bash
# Install Node.js dependencies (includes TailwindCSS and DaisyUI)
npm install

# Build CSS (one-time build)
npx tailwindcss -i ./static/css/input.css -o ./static/css/dist/output.css
```

**Note**: The project uses [DaisyUI](https://daisyui.com/) as a component library for Tailwind CSS. All UI components (buttons, cards, forms, etc.) use DaisyUI classes.

## Daily Development Workflow

Once initial setup is complete, you'll need two terminals running simultaneously for development:

### Terminal 1: Django Development Server

```bash
python manage.py runserver
```

The server will be available at `http://localhost:8000/`

### Terminal 2: TailwindCSS Watcher

Run the TailwindCSS watcher to automatically rebuild CSS when you make changes to templates or styles:

```bash
npx tailwindcss -i ./static/css/input.css -o ./static/css/dist/output.css --watch
```

The watcher will automatically detect changes to:
- Template files (`.html`)
- Input CSS file (`static/css/input.css`)
- TailwindCSS configuration (`tailwind.config.js`)
- DaisyUI theme settings

## Database Management

### About SQLite

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
python manage.py loaddata terrains
python manage.py loaddata building_types
python manage.py loaddata buildings
python manage.py loaddata milestones
python manage.py loaddata milestone_conditions
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
