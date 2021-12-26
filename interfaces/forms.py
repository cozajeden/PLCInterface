from django import forms


class OrderForm(forms.Form):
    """
    Form for ordering
    """
    number = forms.IntegerField(label='Numer zamówienia', min_value=1)
    amount = forms.IntegerField(label='Ilość sztuk do wyprodukowania', min_value=1)