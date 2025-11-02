from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("account:login")
