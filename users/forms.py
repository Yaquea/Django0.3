from django import forms
from .models import User

# Creates a ModelForm class for user signup
class SignupForm(forms.ModelForm):
    # Adds two password fields with PasswordInput widgets
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        # Specifies the model to use
        model = User
        # Specifies the fields to include in the form
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_password2(self):
        # Retrieves both password fields
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        # Validates that both passwords match
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don’t match.")

        return password2  # Always return the cleaned data
