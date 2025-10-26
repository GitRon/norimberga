import pytest

from apps.city.tests.fixtures import ruins_building  # noqa: F401


@pytest.fixture(scope="session")
def django_db_setup():
    """Configure the database for tests."""
