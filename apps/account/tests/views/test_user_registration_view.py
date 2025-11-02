import pytest
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.mark.django_db
def test_user_registration_view_get_displays_registration_form(client):
    """Test UserRegistrationView displays registration form."""
    response = client.get(reverse("account:register"))

    assert response.status_code == 200
    assert "account/register.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_user_registration_view_post_with_valid_data_creates_user(client):
    """Test UserRegistrationView creates user with valid data."""
    data = {
        "username": "newuser",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password1": "securepassword123",
        "password2": "securepassword123",
    }

    response = client.post(reverse("account:register"), data=data, follow=False)

    assert response.status_code == 302
    assert User.objects.filter(username="newuser").exists()
    user = User.objects.get(username="newuser")
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john@example.com"
    assert user.check_password("securepassword123")


@pytest.mark.django_db
def test_user_registration_view_logs_in_user_after_registration(client):
    """Test UserRegistrationView logs in user after successful registration."""
    data = {
        "username": "newuser",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password1": "securepassword123",
        "password2": "securepassword123",
    }

    response = client.post(reverse("account:register"), data=data, follow=True)

    assert response.status_code == 200
    assert response.wsgi_request.user.is_authenticated
    assert response.wsgi_request.user.username == "newuser"


@pytest.mark.django_db
def test_user_registration_view_redirects_to_savegame_list_when_no_savegame(client):
    """Test UserRegistrationView redirects to savegame list when user has no savegame."""
    data = {
        "username": "newuser",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password1": "securepassword123",
        "password2": "securepassword123",
    }

    response = client.post(reverse("account:register"), data=data, follow=False)

    assert response.status_code == 302
    assert response.url == reverse("savegame:savegame-list")


@pytest.mark.django_db
def test_user_registration_view_redirects_to_landing_page_with_existing_savegame(client):
    """Test UserRegistrationView redirects to landing page when user has existing savegame."""
    from unittest.mock import patch

    data = {
        "username": "newuser",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password1": "securepassword123",
        "password2": "securepassword123",
    }

    # Mock the Savegame.objects.filter().exists() to return True
    # This simulates the case where the user has an existing savegame after registration
    with patch("apps.account.views.user_registration_view.Savegame.objects.filter") as mock_filter:
        mock_filter.return_value.exists.return_value = True

        response = client.post(reverse("account:register"), data=data, follow=False)

    assert response.status_code == 302
    assert response.url == reverse("city:landing-page")
