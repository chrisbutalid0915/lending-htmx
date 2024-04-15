from django.contrib import admin
from .models import Loan, LoanProduct, LoanTerm, LoanAmortization, Payment

# Register your models here.


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = [
        "loan_number",
        "loan_amount",
        # "total_paid_interest",
        # "total_paid_principal",
        # "remaining_interest_balance",
        # "remaining_principal_balance",
    ]
    # fields = [*]
    readonly_fields = [
        # "transaction",
        "loan_number",
        "monthly_payment",
        "loan_terms",
        "interest_rate",
        "approval_date",
        "release_date",
        "maturity_date",
        "cancelled_date",
        "fully_paid_date",
        # "total_paid_interest",
        # "total_paid_principal",
    ]


@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    list = ["loan_product"]


@admin.register(LoanTerm)
class LoanTermsAdmin(admin.ModelAdmin):
    list = ["loan_product"]


@admin.register(LoanAmortization)
class LoanAmortizationAdmin(admin.ModelAdmin):
    list = ["*"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list = ["*"]
