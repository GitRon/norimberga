import pytest
from django.urls import reverse


# UserLoginView Tests
@pytest.mark.django_db
def test_user_login_view_get_displays_login_form(client):
    """Test UserLoginView displays login form."""
    response = client.get(reverse("account:login"))

    assert response.status_code == 200
    assert "account/login.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_user_login_view_post_with_valid_credentials(client, user):
    """Test UserLoginView logs in user with valid credentials."""
    user.set_password("testpassword123")
    user.save()

    response = client.post(
        reverse("account:login"), data={"username": "testuser", "password": "testpassword123"}, follow=True
    )

    assert response.status_code == 200
    assert response.wsgi_request.user.is_authenticated
    assert response.wsgi_request.user == user


@pytest.mark.django_db
def test_user_login_view_post_with_invalid_credentials(client, user):
    """Test UserLoginView rejects invalid credentials."""
    user.set_password("testpassword123")
    user.save()

    response = client.post(reverse("account:login"), data={"username": "testuser", "password": "wrongpassword"})

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated
    assert response.context["form"].errors


@pytest.mark.django_db
def test_user_login_view_redirects_to_landing_page_after_login(client, user):
    """Test UserLoginView redirects to landing page after successful login."""
    user.set_password("testpassword123")
    user.save()

    response = client.post(
        reverse("account:login"), data={"username": "testuser", "password": "testpassword123"}, follow=False
    )

    assert response.status_code == 302
    assert response.url == reverse("city:landing-page")


# UserLogoutView Tests
@pytest.mark.django_db
def test_user_logout_view_logs_out_user(authenticated_client, user):
    """Test UserLogoutView logs out authenticated user."""
    response = authenticated_client.post(reverse("account:logout"), follow=True)

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_user_logout_view_redirects_to_login_page(authenticated_client):
    """Test UserLogoutView redirects to login page."""
    response = authenticated_client.post(reverse("account:logout"), follow=False)

    assert response.status_code == 302
    assert response.url == reverse("account:login")


# UserRegistrationView Tests
@pytest.mark.django_db
def test_user_registration_view_get_displays_registration_form(client):
    """Test UserRegistrationView displays registration form."""
    response = client.get(reverse("account:register"))

    assert response.status_code == 200
    assert "account/register.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_user_registration_view_post_with_valid_data_creates_user(client):
    """Test UserRegistrationView creates user with valid data."""
    from django.contrib.auth.models import User

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
def test_user_registration_view_requires_first_name(client):
    """Test UserRegistrationView requires first_name field."""
    data = {
        "username": "newuser",
        "first_name": "",
        "last_name": "Doe",
        "email": "john@example.com",
        "password1": "securepassword123",
        "password2": "securepassword123",
    }

    response = client.post(reverse("account:register"), data=data)

    assert response.status_code == 200
    assert "first_name" in response.context["form"].errors


@pytest.mark.django_db
def test_user_registration_view_requires_last_name(client):
    """Test UserRegistrationView requires last_name field."""
    data = {
        "username": "newuser",
        "first_name": "John",
        "last_name": "",
        "email": "john@example.com",
        "password1": "securepassword123",
        "password2": "securepassword123",
    }

    response = client.post(reverse("account:register"), data=data)

    assert response.status_code == 200
    assert "last_name" in response.context["form"].errors


@pytest.mark.django_db
def test_user_registration_view_validates_password_match(client):
    """Test UserRegistrationView validates that passwords match."""
    data = {
        "username": "newuser",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password1": "securepassword123",
        "password2": "differentpassword",
    }

    response = client.post(reverse("account:register"), data=data)

    assert response.status_code == 200
    assert "password2" in response.context["form"].errors


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
    with patch("apps.account.views.Savegame.objects.filter") as mock_filter:
        mock_filter.return_value.exists.return_value = True

        response = client.post(reverse("account:register"), data=data, follow=False)

    assert response.status_code == 302
    assert response.url == reverse("city:landing-page")
