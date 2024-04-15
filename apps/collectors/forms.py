from django import forms
from .models import Collector
from dynamic_forms import DynamicFormMixin


class CollectorForm(DynamicFormMixin, forms.ModelForm):
    class Meta:
        model = Collector
        fields = (
            "full_name",
            "contact_no",
            "is_active",
            # "approval_date",
            # "maturity_date",
            # "status"
        )