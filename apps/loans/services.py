from .models import (
    Loan,
    LoanAmortization,
    Payment,
    Transaction,
    TransactionEntry,
    LedgerAccount,
)
from dateutil.relativedelta import relativedelta
from .utils import calculate_loan_payment
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from datetime import datetime


def generate_amortization_schedule(loan: Loan):
    loan_amount = loan.loan_amount
    terms = loan.loan_terms
    interest_rate = loan.interest_rate / 100  # convert from percentage to decimal
    monthly_interest_rate = interest_rate / terms  # get monthly interest
    monthly_payment = calculate_loan_payment(
        interest_rate=interest_rate, terms=terms, loan_amount=loan_amount
    )  # compute the monthly payment

    balance = loan_amount  # set running balance
    amortization_schedule = []
    for _, index in enumerate(range(terms)):
        interest = balance * monthly_interest_rate  # get the monthly interest
        principal_amount = monthly_payment - interest  # get the principal amount
        balance -= principal_amount  # compute the running balance

        round_off_balance = Decimal(balance).quantize(
            Decimal("0.00"), rounding=ROUND_HALF_UP
        )  # rounding off

        if -1 < round_off_balance < 1:  # remove zero negative
            round_off_balance = abs(round_off_balance)

        maturity_date = None
        if loan.release_date:
            maturity_date = loan.release_date + relativedelta(months=index + 1)

        amortization_schedule.append(
            {
                "loan": loan,
                "term": index + 1,
                "maturity_date": maturity_date,
                "principal_amount": monthly_payment - interest,
                "interest_amount": interest,
                "total": principal_amount + interest,
                "running_balance": balance,
            }
        )  # append to list
    # print(amortization_schedule)
    return amortization_schedule


def auto_create_loan_product_ledger_account():
    pass


def create_payment_transaction(payment: Payment):
    transaction_type = "or"
    transaction = Transaction.objects.create(
        transaction_no=payment.transaction, transaction_type=transaction_type
    )

    payment.transaction = transaction

    result = calculate_due_payment(payment.loan)
    print(result)
    print(result["total_principal_amount"])
    print(result["total_interest_amount"])

    to_pay_interest_amount = result["total_interest_amount"]
    to_pay_principal_amount = payment.amount - result["total_interest_amount"]

    TransactionEntry.objects.update_or_create(
        transaction=transaction,
        entry_type="d",
        ledger_account=payment.loan.terms.ledger_account,
        defaults={"amount": to_pay_interest_amount},
    )

    TransactionEntry.objects.update_or_create(
        transaction=transaction,
        entry_type="d",
        ledger_account=payment.loan.loan_product.ledger_account,
        defaults={"amount": to_pay_principal_amount},
    )

    TransactionEntry.objects.update_or_create(
        transaction=transaction,
        entry_type="c",
        defaults={
            "ledger_account": LedgerAccount.objects.get(account_number=100001),
            "amount": payment.loan_amount,
        },
    )


def calculate_due_payment(loan: Loan):
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d")
    loan_amortization = LoanAmortization.objects.filter(loan=loan).order_by(
        "maturity_date"
    )
    amortization_due_date = loan_amortization.filter(maturity_date__gte=formatted_date)
    amort_date = amortization_due_date.first().maturity_date.strftime("%Y-%m-%d")
    amortization = loan_amortization.filter(maturity_date__lte=amort_date)
    total_principal_amount = amortization.aggregate(
        principal_amount=Sum("principal_amount")
    )["principal_amount"]
    total_interest_amount = amortization.aggregate(
        interest_amount=Sum("interest_amount")
    )["interest_amount"]
    result = {
        "total_principal_amount": total_principal_amount,
        "total_interest_amount": total_interest_amount,
    }
    return result


def get_total_due_amount(date):
    loan_amortization = LoanAmortization.objects.filter(maturity_date__lte=date)
    total_due_amount = loan_amortization.aggregate(total_amount=Sum('total'))['total_amount'] or 0
    return total_due_amount


def get_total_payment():
    total_payment = Payment.objects.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    return total_payment


def get_total_loan_release():
    status = Loan.LoanStatus.released
    total = Loan.objects.filter(status=status).aggregate(total_amount=Sum('loan_amount'))['total_amount'] or 0
    return total


def get_loan_release_per_year(year):
    status = Loan.LoanStatus.released
    loan_releases = Loan.objects.filter(status=status, release_date__year=year).annotate(month=ExtractMonth('release_date')) \
                            .values('month') \
                            .annotate(total_amount=Sum('loan_amount'))
    return loan_releases


def get_year_min():
    status = Loan.LoanStatus.released
    loan_release = Loan.objects.filter(status=status).order_by('release_date').first()
    if loan_release:
        return loan_release.release_date.year
    return datetime.now().year

def get_year_max():
    status = Loan.LoanStatus.released
    loan_release =  Loan.objects.filter(status=status).order_by('-release_date').first()
    if loan_release:
        return loan_release.release_date.year
    return datetime.now().year