# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Norimberga is a browser-based city simulation game set in the high middle ages, focusing on space management challenges within city walls. Built with Django 5.2, it uses a mono-app architecture approach with TailwindCSS for styling and HTMX for interactivity.

## Development Commands

### Environment Setup (uv)
```bash
# Install dependencies
uv sync

# Install with development dependencies
uv sync --group dev

# Add a new dependency
uv add django-extensions

# Add a development dependency
uv add --dev pytest-mock

# Update dependencies
uv lock --upgrade

# Create virtual environment and install dependencies
uv venv && uv sync --group dev
```

### Backend (Django)
```bash
# Database migrations
python manage.py migrate

# Run development server
python manage.py runserver

# Create new migrations after model changes
python manage.py makemigrations

# Custom management commands
python manage.py list_templates  # List template files for Tailwind
```

### Testing (PyTest)
```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest apps/city/tests/test_models.py

# Run tests with coverage report
pytest --cov=apps --cov-report=html --cov-report=term-missing

# Run tests in parallel (faster)
pytest -n auto

# Run tests and generate coverage report only
pytest --cov=apps --cov-report=html

# View coverage report (after running tests with --cov-report=html)
# Open htmlcov/index.html in browser
```

### Frontend (TailwindCSS)
```bash
# Build and watch CSS changes during development
npx tailwindcss -i ./static/css/input.css -o ./static/css/dist/output.css --watch
```

### Code Quality
```bash
# Lint with ruff (configured in pyproject.toml)
ruff check

# Format with ruff
ruff format

# Run boa-restrictor linter (custom Python and Django linter)
pre-commit run --all-files boa-restrictor

# Run all pre-commit hooks
pre-commit run --all-files
```
## Architecture

**IMPORTANT**: Follow the established patterns documented in `docs/patterns/` for all code. This includes:
- Mono-app approach (`docs/patterns/mono_app_approach.md`)
- Service pattern (`docs/patterns/services.md`)
- Dependency injection (`docs/patterns/dependency_injection.md`)
- ORM structure (`docs/patterns/orm_structure.md`)
- Testing strategy (`docs/patterns/testing_strategy.md`)

### Mono-App Approach
The project follows a mono-app pattern where most business logic lives in the main `city` app. Key principles:
- Self-contained Django apps that could theoretically be moved to other projects
- Main app (`city`) can import satellite apps, but not vice versa
- Avoid circular dependencies between apps

### App Structure
- `apps/city/` - Main game logic (buildings, tiles, savegames)
- `apps/event/` - Event system for game occurrences
- `apps/milestone/` - Achievement/milestone tracking
- `apps/round/` - Game round management
- `apps/config/` - Django settings and configuration
- `apps/core/` - Shared utilities and base classes

### Service Pattern
Business logic is organized into service classes following these conventions:
- Services have a `process()` method as entry point
- Use protected methods (underscore prefix) for internal logic
- Name ends with "Service" (e.g., `HelloWorldService`)
- Services don't query the database directly - use selectors/managers
- Located in `[app]/services/[service_name].py`

### Dependency Injection
External APIs and third-party integrations use abstract base classes for dependency injection, allowing for fake implementations during development and testing.

## Key Models

### City App Models
- `Savegame` - Game state (city_name, coins, population, unrest, current_year)
- `Terrain` - Map terrain types with building restrictions
- `BuildingType` - Building templates with costs and properties
- `Building` - Actual building instances on the map
- `Tile` - Map grid coordinates with terrain and buildings

### Game Mechanics
- Buildings have maintenance costs and generate taxes
- Population management with housing constraints
- Unrest system (0-100 scale)
- Tile-based map with coordinate system

## Testing Strategy

Uses PyTest exclusively for backend testing. Key guidelines:
- Each Django app has its own `tests/` package - no global test directory
- One test file contains test functions for one testee (usually a Python class)
- Use function-based tests, not class-based tests (pytest best practice)
- Test function naming: `test_[TESTEE]_[TEST_CASE]`
- Always use factory_boy factories instead of creating objects directly
- Follow AAA pattern (Arrange/Act/Assert) in test functions
- Avoid mocking first-party code when possible

## Technology Stack

### Backend
- Django 5.2 with SQLite database
- django-crispy-forms with crispy-tailwind for form styling
- uv for dependency management
- Python 3.13+

### Frontend
- TailwindCSS 3.4 with custom config
- HTMX 1.9 for interactivity
- Toastify.js for notifications
- Custom Tailwind plugins: @tailwindcss/forms, tailwindcss-bg-patterns

### Testing
- PyTest 7.4+ with pytest-django for Django integration
- pytest-cov for coverage reporting (minimum 80% coverage required)
- factory-boy for test data generation
- pytest-xdist for parallel test execution

### Development Tools
- Ruff for linting and formatting (configured with extensive rule set)
- Boa-restrictor for Python and Django linting
- Pre-commit hooks with django-upgrade, djhtml for template formatting
- Import-linter for architecture enforcement (referenced but not configured)

## File Locations

### Static Files
- `static/css/input.css` - TailwindCSS source file
- `static/css/dist/output.css` - Compiled CSS output
- Node modules in `node_modules/` also served as static files

### Templates
- App-specific templates in `apps/[app]/templates/[app]/`
- Custom context processor for savegame data access

### Tests
- Each Django app has its own `tests/` package (e.g., `apps/city/tests/`)
- Factory definitions in `apps/[app]/tests/factories.py`
- App-specific configuration in `apps/[app]/tests/conftest.py`
- Coverage reports generated in `htmlcov/` directory

### Configuration
- Main settings: `apps/config/settings.py`
- URL routing: `apps/config/urls.py`
- Dependencies: `pyproject.toml` (main) and `requirements*.txt` (uv compatibility)
- Ruff config in `pyproject.toml`
- TailwindCSS config in `tailwind.config.js`
- PyTest config in `pyproject.toml` under `[tool.pytest.ini_options]`

## Development Workflow

1. Set up environment: `uv sync --group dev`
2. Run backend server: `python manage.py runserver`
3. In separate terminal, watch TailwindCSS: `npx tailwindcss -i ./static/css/input.css -o ./static/css/dist/output.css --watch`
4. Make changes to code
5. Run migrations after model changes: `python manage.py makemigrations && python manage.py migrate`
6. Run tests: `pytest`
7. Before committing: `pre-commit run --all-files` or rely on pre-commit hooks

## Important Notes

- Django settings use insecure secret key - only for development
- Database is SQLite for development simplicity
- Custom management commands available for map generation and template listing
- TailwindCSS config dynamically includes template files via Django command
- Pre-commit hooks run on pre-push stage to allow faster commits during development
