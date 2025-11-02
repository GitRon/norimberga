import pytest
from django.urls import reverse


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
