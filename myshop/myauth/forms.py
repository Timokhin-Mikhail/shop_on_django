from django import forms


class UpBalanceForm(forms.Form):
    up_balance_count = forms.IntegerField(min_value=0)


