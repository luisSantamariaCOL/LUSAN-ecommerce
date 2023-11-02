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

    class Meta:
        # Link the form to the Account model
        model = Account
        # Define the fields that will be included in the form
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']
