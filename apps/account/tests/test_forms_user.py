import pytest
from django.contrib.auth.models import User

from apps.account.forms.user import UserRegistrationForm


@pytest.mark.django_db
def test_user_registration_form_valid_data():
    """Test UserRegistrationForm with valid data."""
    form_data = {
        "username": "testuser",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password1": "securepassword123",
        "password2": "securepassword123",
    }

    form = UserRegistrationForm(data=form_data)

    assert form.is_valid()


@pytest.mark.django_db
def test_user_registration_form_creates_user():
    """Test UserRegistrationForm saves user correctly."""
    form_data = {
        "username": "testuser",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password1": "securepassword123",
        "password2": "securepassword123",
    }

    form = UserRegistrationForm(data=form_data)
    assert form.is_valid()

    user = form.save()

    assert user.username == "testuser"
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john@example.com"
    assert user.check_password("securepassword123")
    assert User.objects.filter(username="testuser").exists()


@pytest.mark.django_db
def test_user_registration_form_requires_first_name():
    """Test UserRegistrationForm requires first_name field."""
    form_data = {
        "username": "testuser",
        "first_name": "",
        "last_name": "Doe",
        "email": "john@example.com",
        "password1": "securepassword123",
        "password2": "securepassword123",
    }

    form = UserRegistrationForm(data=form_data)

    assert not form.is_valid()
    assert "first_name" in form.errors


@pytest.mark.django_db
def test_user_registration_form_requires_last_name():
    """Test UserRegistrationForm requires last_name field."""
    form_data = {
        "username": "testuser",
        "first_name": "John",
        "last_name": "",
        "email": "john@example.com",
        "password1": "securepassword123",
        "password2": "securepassword123",
    }

    form = UserRegistrationForm(data=form_data)

    assert not form.is_valid()
    assert "last_name" in form.errors


@pytest.mark.django_db
def test_user_registration_form_validates_password_match():
    """Test UserRegistrationForm validates that passwords match."""
    form_data = {
        "username": "testuser",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password1": "securepassword123",
        "password2": "differentpassword",
    }

    form = UserRegistrationForm(data=form_data)

    assert not form.is_valid()
    assert "password2" in form.errors


@pytest.mark.django_db
def test_user_registration_form_email_optional():
    """Test UserRegistrationForm allows optional email."""
    form_data = {
        "username": "testuser",
        "first_name": "John",
        "last_name": "Doe",
        "email": "",
        "password1": "securepassword123",
        "password2": "securepassword123",
    }

    form = UserRegistrationForm(data=form_data)

    assert form.is_valid()


@pytest.mark.django_db
def test_user_registration_form_hashes_password():
    """Test UserRegistrationForm hashes the password properly."""
    form_data = {
        "username": "testuser",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password1": "securepassword123",
        "password2": "securepassword123",
    }

    form = UserRegistrationForm(data=form_data)
    assert form.is_valid()

    user = form.save()

    # Password should be hashed, not stored in plain text
    assert user.password != "securepassword123"
    assert user.check_password("securepassword123")
