from django import forms

from . import models


class OrderForm(forms.ModelForm):
    """
    Form for ordering
    """

    class Meta:
        model = models.Order
        fields = ['number', 'requested_amount']
        labels = {
            'number': 'Numer zamówienia',
            'requested_amount': 'Ilość sztuk do wyprodukowania',
        }