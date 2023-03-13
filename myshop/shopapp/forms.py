from django import forms
from django.forms import ModelForm
from shopapp.models import Order


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'promocode']


class UploadProductsForms(forms.Form):
    file = forms.FileField()

