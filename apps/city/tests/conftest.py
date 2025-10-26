import pytest


@pytest.fixture(scope="session")
def django_db_setup():
    """Configure the database for tests."""
