from django import forms
from .models import Order
class CartForm(forms.Form):
    quantity = forms.IntegerField(initial='1', min_value=1)
    product_id = forms.IntegerField(widget=forms.HiddenInput)
    CHOICES = ((0, 'Internal'),(1, 'External'), (2, 'Staff'))
    price = forms.ChoiceField(choices=CHOICES)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(CartForm, self).__init__(*args, **kwargs)


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('paid', 'ticket_id',)

        widgets = {
            'address': forms.Textarea(attrs={'row': 5, 'col': 8}),
        }
