from django import forms
from .models import LedgerAccount


class LedgerAccountForm(forms.ModelForm):
    class Meta:
        model = LedgerAccount
        fields = (
            "ledger_type",
            "account_title",
            # "account_number",
            "description",
            "status",
        )