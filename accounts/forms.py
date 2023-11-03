from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm):
    """
    A Django form for registering a new user account.

    This form is linked to the Account model and includes fields for first name, last name,
    phone number, email, and password. It utilizes Django's ModelForm functionality to 
    generate fields directly from the model and to handle form-to-model data saving.

    Attributes:
    - Meta: A class containing metadata for the form.
        - model: The model to which the form is linked.
        - fields: A list of field names to include in the form from the Account model.
    """

    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    

    class Meta:
        # Link the form to the Account model
        model = Account
        # Define the fields that will be included in the form
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

