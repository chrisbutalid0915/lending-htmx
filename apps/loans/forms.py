from django import forms
from apps.clients.models import Client
from .models import Loan, LoanProduct, LoanTerm, Payment
from dynamic_forms import DynamicField, DynamicFormMixin
from dateutil.relativedelta import relativedelta
from datetime import datetime


class LoanForm(DynamicFormMixin, forms.ModelForm):
    def term_choices(self):
        loan_product = self["loan_product"].value()
        return LoanTerm.objects.filter(loan_product=loan_product, status=True)

    def initial_term(self):
        loan_product = self["loan_product"].value()
        return LoanTerm.objects.filter(loan_product=loan_product, status=True).first()

    def get_end_date(self):
        loan_date = str(self["start_date"].value())
        loan_date = datetime.strptime(loan_date, "%Y-%m-%d").date()
        end_date = loan_date + relativedelta(months=5)
        formatted_date = end_date.strftime("%B %d, %Y")
        return formatted_date

    client = forms.ModelChoiceField(
        queryset=Client.objects.all(), initial=None
    )

    loan_product = forms.ModelChoiceField(
        queryset=LoanProduct.objects.all(), initial=None
    )

    terms = DynamicField(
        forms.ModelChoiceField, queryset=term_choices, initial=initial_term
    )

    class Meta:
        model = Loan
        fields = (
            "client",
            "loan_product",
            "terms",
            "loan_amount",
            "interest_amount",
            # "approval_date",
            # "maturity_date",
            # "status"
        )

        widgets = {
            "interest_amount": forms.TextInput(attrs={"readonly": "readonly"}),
        }


class LoanProductForm(forms.ModelForm):
    class Meta:
        model = LoanProduct
        fields = (
            "loan_product",
            "description",
            "penalty",
        )


class PaymentForm(forms.ModelForm):
    status = Loan.LoanStatus.released
    loan = forms.ModelChoiceField(
        queryset=Loan.objects.filter(status=status)
    )

    class Meta:
        model = Payment
        fields = (
            "loan",
            "payment_method",
            "amount",
            "description",
        )
