import pytest
from django.urls import reverse


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
