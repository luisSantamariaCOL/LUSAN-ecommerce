from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'email_address_line_1', 'email_address_line_2', 'country', 'state', 'city', 'order_note']