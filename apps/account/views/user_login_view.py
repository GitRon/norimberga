from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator


@method_decorator(login_not_required, name="dispatch")
class UserLoginView(LoginView):
    template_name = "account/login.html"
    next_page = reverse_lazy("city:landing-page")
