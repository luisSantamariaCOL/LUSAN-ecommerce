from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm):
    # Moved password fields to the top to improve readability
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password', 'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'}))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter First Name', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter Last Name', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Email Address', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter Phone Number', 'class': 'form-control'}),
            # Password field does not need to be redefined here as it is already customized above
        }

    def clean(self):
        cleaned_data = super().clean()  # No need to specify the class name explicitly
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match!")
            # It's better to use add_error for field-specific validation messages

        return cleaned_data  # Always return the cleaned data at the end of the clean method