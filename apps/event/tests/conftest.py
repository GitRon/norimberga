import pytest


@pytest.fixture
def mock_random_value():
    """Fixture to control random.randint behavior in tests."""
    return 50
