from django.contrib.auth import login
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic

from apps.account.forms.user import UserRegistrationForm
from apps.savegame.models import Savegame


@method_decorator(login_not_required, name="dispatch")
class UserLoginView(LoginView):
    template_name = "account/login.html"
    next_page = reverse_lazy("city:landing-page")


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("account:login")


@method_decorator(login_not_required, name="dispatch")
class UserRegistrationView(generic.CreateView):
    form_class = UserRegistrationForm
    template_name = "account/register.html"

    def form_valid(self, form) -> HttpResponse:
        # Save the user
        user = form.save()

        # Log the user in
        login(self.request, user)

        # Check if user has any savegames
        has_savegame = Savegame.objects.filter(user=user).exists()

        # Redirect to savegame list if no savegame exists, otherwise to landing page
        if has_savegame:
            return HttpResponseRedirect(reverse_lazy("city:landing-page"))

        return HttpResponseRedirect(reverse_lazy("savegame:savegame-list"))
