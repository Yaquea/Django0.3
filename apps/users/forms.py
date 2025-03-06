from django import forms
from .models import User
from PIL import Image  # Used to validate image dimensions

# ModelForm for user signup
class Signup_Form(forms.ModelForm):
    # Two password fields with PasswordInput widgets for secure password entry
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        # Specifies the model to use
        model = User
        # Specifies the fields to include in the form
        fields = ['username', 'first_name', 'last_name', 'email', 'profile_image']

    def clean_profile_image(self):
        image_file = self.cleaned_data.get('profile_image')

        if image_file:
            # Validate file size
            max_size = 2 * 1024 * 1024  # 2 MB
            if image_file.size > max_size:
                raise forms.ValidationError("The image must not exceed 2MB.")

            # Validate image dimensions
            img = Image.open(image_file)
            max_width = 1024
            max_height = 1024
            if img.width > max_width or img.height > max_height:
                # Raise an error if the image dimensions are bigger than the maximum dimenssions
                raise forms.ValidationError(
                    f"The image must be a maximum of {max_width}x{max_height} pixels."
                )

            # Reset the file pointer to the beginning to avoid stream issues
            image_file.seek(0)

        return image_file

    def clean_password2(self):
        # Retrieve both password fields
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        # Validate that both passwords match
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")

        return password2  # Always return the cleaned data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if the email is already in use
        if User.objects.filter(email=email).exists():
            # If not raise an error
            raise forms.ValidationError("This email address is already in use.")
        return email


# ModelForm for resending the verification email
class Resend_Verification_Email_Form(forms.ModelForm):
    class Meta:
        # Specifies the model to use
        model = User
        # Specifies the field to include in the form
        fields = ['email']


# ModelForm for updating user information
class UserUpdateForm(forms.ModelForm):
    class Meta:
        # Specifies the model to use
        model = User
        # Specifies the model fields to use
        fields = ['username', 'first_name', 'last_name', 'email', 'profile_image']

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')

        if image:
            # Validate file size
            max_size = 2 * 1024 * 1024  
            if image.size > max_size:
                raise forms.ValidationError("The image must not exceed 2MB.")

            # Validate image dimensions
            img = Image.open(image)
            max_width, max_height = 1024, 1024
            if img.width > max_width or img.height > max_height:
                # Raise an error if the image dimensions are bigger than the maximum dimenssions
                raise forms.ValidationError(
                    f"The image must be a maximum of {max_width}x{max_height} pixels."
                )

        return image
