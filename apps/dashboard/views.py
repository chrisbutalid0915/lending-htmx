from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from .forms import DashboardForm
from django.http import JsonResponse
from apps.loans.services import get_total_loan_release, get_total_payment, get_total_due_amount, get_loan_release_per_year, get_year_min
from datetime import datetime
from decimal import Decimal
from apps.transactions.models import Transaction, TransactionEntry
from apps.loans.models import Loan, Payment
from apps.clients.models import Client

currency_sign = '₱'

# Create your views here.
class DashboardView(LoginRequiredMixin, ListView):
    login_url = "users:login"
    
    template_name = "dashboard/dashboard.html"

    redirect_field_name = "dashboard:dashboard"
    form_class = DashboardForm

    def get_queryset(self):
        return None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()  # Pass an instance of your form to the context
        return context
    

def donut_chart_statistic(request):
    print('get stat donut')
    now = datetime.now()
    total_loan_release = get_total_loan_release()
    total_payment = get_total_payment()
    due_amount = get_total_due_amount(now)
    total_due_amount = due_amount - total_payment

    labels = ["Loan Releases", "Payment", "Due Amount"]
    data = [total_loan_release, total_payment, total_due_amount]
    
    chart_data = {
        'labels': labels,
        'data': data 
    }
    return JsonResponse(chart_data)


def bar_chart_statistic(request):
    print("get bar chart")
    # year = 2024
    year = request.GET.get("year")
    if year is None:
        year = get_year_min()
    print(year)
    loan_releases = get_loan_release_per_year(year)

    labels = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    data = [0] * len(labels)

    for loan_release in loan_releases:
        month_index = loan_release['month'] - 1
        data[month_index] = float(loan_release['total_amount'])

    chart_data = {
        'labels': labels,
        'data': data
    }

    return JsonResponse(chart_data)


def recent_loan_activity(request):
    loans = Loan.objects.all().order_by("-updated_at")[:5]
    context = {"loans": loans, "currency_sign": currency_sign}

    return render(request, "dashboard/partials/recent-loan.html", context)


def recent_payment_activity(request):
    payments = Payment.objects.all().order_by("-updated_at")[:5]
    context = {"payments": payments, "currency_sign": currency_sign}

    return render(request, "dashboard/partials/recent-payment.html", context)


def recent_client(request):
    clients = Client.objects.all().order_by("-updated_at")[:5]
    context = {"clients": clients}

    return render(request, "dashboard/partials/recent-client.html", context)
