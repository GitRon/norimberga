from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout, Submit
from django import forms
from django.contrib.auth.models import User


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        help_text="Enter a secure password",
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
        help_text="Enter the same password again for verification",
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        labels = {
            "username": "Username",
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email",
        }
        help_texts = {
            "username": "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
            "email": "Optional. Enter a valid email address.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make first_name and last_name required
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

        self.helper = FormHelper()
        self.helper.form_id = "id_user_registration_form"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("username"),
            Field("first_name"),
            Field("last_name"),
            Field("email"),
            Field("password1"),
            Field("password2"),
            Div(
                Submit(
                    "submit",
                    "Register",
                    css_class="w-full px-4 py-2 bg-lime-600 text-white text-sm font-medium rounded-md "
                    "hover:bg-lime-700 focus:outline-none focus:ring-2 focus:ring-offset-2 "
                    "focus:ring-lime-500",
                ),
                css_class="mt-6",
            ),
        )

    def clean_password2(self) -> str:
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True) -> User:  # noqa: FBT002
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
