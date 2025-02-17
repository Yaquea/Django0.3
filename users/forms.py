from django import forms
from .models import User
from PIL import Image  # To check image dimensions

# Creates a ModelForm class for user signup
class Signup_Form(forms.ModelForm):
    # Adds two password fields with PasswordInput widgets
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
            # 1. Validar el tamaño del archivo (máximo 2MB)
            max_size = 2 * 1024 * 1024  # 2 MB
            if image_file.size > max_size:
                raise forms.ValidationError("The image must not exceed 2MB.")

        # 2. Validar las dimensiones de la imagen usando PIL
            img = Image.open(image_file)
            max_width = 1024
            max_height = 1024
            if img.width > max_width or img.height > max_height:
                raise forms.ValidationError(
                    f"The image must be a maximum of {max_width}x{max_height} pixels."
                )

        # Reinicia el puntero del archivo para que no esté al final del stream
            image_file.seek(0)

        return image_file


    def clean_password2(self):
        # Retrieves both password fields
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        # Validates that both passwords match
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don’t match.")

        return password2  # Always return the cleaned data
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

class Resend_Verification_Email_Form(forms.ModelForm):
    class Meta:
        # Specifies the model to use
        model = User
        # Specifies the fields to include in the form
        fields = ['email']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name', 'last_name', 'email', 'profile_image']

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')

        if image:
            max_size = 2 * 1024 * 1024  
            if image.size > max_size:
                raise forms.ValidationError("The image must not exceed 2MB.")

            img = Image.open(image)
            max_width, max_height = 1024, 1024
            if img.width > max_width or img.height > max_height:
                raise forms.ValidationError(f"The image must be a maximum of {max_width}x{max_height} pixels.")

        return image

