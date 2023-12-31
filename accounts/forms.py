from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm):
    # Custom password fields with placeholders and bootstrap class
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password', 'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'}))

    class Meta:
        model = Account # Specify the model for form generation
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']

        # Custom widgets with placeholders and bootstrap class for model fields
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter First Name', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter Last Name', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Email Address', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter Phone Number', 'class': 'form-control'}),
        }


    def clean(self):
        # Custom clean method to compare password fields
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # Check if both password entries match
        if password != confirm_password:
            # Raise validation error if there is a mismatch
            raise forms.ValidationError("Password does not match!")



