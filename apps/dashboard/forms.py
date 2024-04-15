from django import forms
from django.db.models import Sum
from apps.clients.models import Client
from apps.loans.models import Loan, Payment, LoanAmortization
from datetime import datetime
from apps.loans.services import get_total_loan_release, get_total_payment, get_total_due_amount, get_year_min, get_year_max
from dynamic_forms import DynamicField, DynamicFormMixin


currency_sign = '₱'

class TotalBorrowersWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        total = Client.objects.count()
        return str(total)


class TotalLoanReleaseWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        total = get_total_loan_release()
        return f'{currency_sign}{total}'
    

class TotalPaymentWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        total = get_total_payment()
        return f'{currency_sign}{total}'
    

class TotalDueAmountWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        now = datetime.now()
        total_due_amount = get_total_due_amount(now)
        total_payment = get_total_payment()
        total = total_due_amount - total_payment
        return f'{currency_sign}{total}'


class YearSelectWidget(forms.Select):
    def __init__(self, attrs=None):
        start_year = get_year_min()
        max_year = get_year_max() + 1

        years = [year for year in range(start_year, max_year)]  # Adjust the range of years as needed
        choices = [(year, str(year)) for year in years]
        super().__init__(attrs, choices)


class DashboardForm(forms.Form):
    year = forms.ChoiceField(choices=[], widget=YearSelectWidget, initial=datetime.now().year)
    total_borrowers = forms.CharField(widget=TotalBorrowersWidget(), disabled=True)
    total_loan_release = forms.CharField(widget=TotalLoanReleaseWidget(), disabled=True)
    total_payment = forms.CharField(widget=TotalPaymentWidget(), disabled=True)
    total_due_amount = forms.CharField(widget=TotalDueAmountWidget(), disabled=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['year'].choices = self.get_year_choices()

    def get_year_choices(self):
        start_year = get_year_min()
        max_year = get_year_max() + 1
        years = [(year, str(year)) for year in range(start_year, max_year)]  # Adjust the range of years as needed
        return years