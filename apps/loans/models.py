import uuid
from django.db import models
from datetime import datetime
from dateutil.relativedelta import relativedelta
from apps.clients.models import Client
from apps.transactions.models import Transaction, TransactionEntry
from apps.ledger_accounts.models import LedgerAccount
from .utils import (
    calculate_loan_interest,
    calculate_loan_payment,
)

# Create your models here.

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LoanProduct(TimeStampedModel):
    loan_product = models.CharField(max_length=150, unique=True)
    description = models.TextField(null=True, blank=True)
    penalty = models.IntegerField(null=True, blank=True)

    ledger_account = models.ForeignKey(
        LedgerAccount, on_delete=models.CASCADE, null=True
    )
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.ledger_account:
            ledger_account = LedgerAccount.objects.create(
                ledger_type="assets",
                account_title=self.loan_product,
            )
            self.ledger_account = ledger_account

        super().save(*args, **kwargs)

    def __str__(self):
        return self.loan_product


class LoanTerm(TimeStampedModel):
    class TermsMonths(models.TextChoices):
        terms_60 = 60, "60"
        terms_48 = 48, "48"
        terms_36 = 36, "36"
        terms_24 = 24, "24"
        terms_18 = 18, "18"
        terms_12 = 12, "12"
        terms_6 = 6, "6"
        terms_3 = 3, "3"

    loan_product = models.ForeignKey(
        LoanProduct, on_delete=models.CASCADE, related_name="loan_product_terms"
    )
    terms = models.IntegerField(
        choices=TermsMonths.choices
    )
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    ledger_account = models.ForeignKey(
        LedgerAccount, on_delete=models.CASCADE, null=True
    )
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        print("Loan terms")
        if not self.ledger_account:
            ledger_account = LedgerAccount.objects.create(
                ledger_type="income",
                account_title="Interest - " + self.loan_product,
            )

            self.ledger_account = ledger_account
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.loan_product} - Months {self.terms} - Interest rate {self.interest_rate}%"


class Loan(TimeStampedModel):
    class LoanStatus(models.TextChoices):
        pending = "pending", "Pending"
        approved = "approved", "Approved"
        cancelled = "cancelled", "Cancelled"
        released = "released", "Released"
        fully_paid = "fully_paid", "Fully Paid"

    transaction = models.OneToOneField(
        Transaction, null=True, blank=True, on_delete=models.CASCADE
    )
    client = models.ForeignKey(Client, null=True, on_delete=models.CASCADE)
    loan_number = models.CharField(max_length=12, editable=False, unique=True)
    loan_product = models.ForeignKey(LoanProduct, on_delete=models.CASCADE, null=True)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=10, null=True, decimal_places=2)
    terms = models.ForeignKey(LoanTerm, null=True, on_delete=models.CASCADE)
    loan_terms = models.IntegerField(null=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    interest_amount = models.DecimalField(
        max_digits=10, null=True, blank=True, decimal_places=2
    )
    approval_date = models.DateField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    maturity_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=25, choices=LoanStatus.choices, default=LoanStatus.pending
    )
    cancelled_date = models.DateField(null=True, blank=True)
    fully_paid_date = models.DateTimeField(null=True)

    @property
    def total_paid_interest(self):
        total = 0
        payments = Payment.objects.filter(loan=self.id).select_related("transaction")
        for p in payments:
            transaction_entry = TransactionEntry.objects.filter(
                transaction=p.transaction.id,
                entry_type="d",
                ledger_account=self.terms.ledger_account,
            )
            
            if transaction_entry:
                total += transaction_entry[0].amount

        return total

    @property
    def total_paid_principal(self):
        total = 0
        payments = Payment.objects.filter(loan=self.id).select_related("transaction")
        for p in payments:
            transaction_entry = TransactionEntry.objects.filter(
                transaction=p.transaction.id,
                entry_type="d",
                ledger_account=self.loan_product.ledger_account,
            )
            if transaction_entry:
                total += transaction_entry[0].amount

        return total

    @property
    def remaining_principal_balance(self):
        return self.loan_amount - self.total_paid_principal

    @property
    def remaining_interest_balance(self):
        return self.interest_amount - self.total_paid_interest

    def create_update_transaction(self):
        transaction_type = "cv"

        # create a transaction for loan
        transaction = Transaction.objects.create(
            transaction_no=self.transaction, transaction_type=transaction_type
        )

        self.transaction = transaction

        # create transaction entry for debit, credit, and cash disbursement
        TransactionEntry.objects.update_or_create(
            transaction=transaction,
            entry_type="d",
            defaults={
                "ledger_account": LedgerAccount.objects.get(account_number=100001),
                "amount": self.loan_amount,
            },
        )

        # create credit loan product
        TransactionEntry.objects.update_or_create(
            transaction=transaction,
            entry_type="c",
            ledger_account=self.loan_product.ledger_account,
            defaults={"amount": self.loan_amount - self.interest_amount},
        )

        # create credit interest
        TransactionEntry.objects.update_or_create(
            transaction=transaction,
            entry_type="c",
            ledger_account=self.terms.ledger_account,
            defaults={"amount": self.interest_amount},
        )

    def save(self, *args, **kwargs):
        if not self.loan_number:  # check if the instance is being created
            self.loan_number = str(uuid.uuid4().hex)[:12].upper()

        if self.status == "pending":
            self.loan_terms = self.terms.terms
            self.interest_rate = self.terms.interest_rate  # insert interest_rate
            interest_rate = self.interest_rate / 100

            # calculate monthly payment
            self.monthly_payment = calculate_loan_payment(
                interest_rate, self.loan_terms, self.loan_amount
            )  

        if self.status == "approved":  # loan approval
            self.approval_date = datetime.now()

        if self.status == "released":  # loan released
            self.release_date = datetime.now()
            self.maturity_date = self.release_date + relativedelta(
                months=self.terms.terms
            )
            if not self.transaction:
                self.create_update_transaction()

        if self.status == "cancelled":  # loan approval
            self.cancelled_date = datetime.now()

        if not self.interest_amount:
            interest_rate = self.interest_rate / 100
            terms = self.loan_terms
            loan_amount = self.loan_amount
            self.interest_amount = calculate_loan_interest(
                interest_rate, terms, loan_amount
            )

        super().save(*args, **kwargs)

    @classmethod
    def update_loan_status(cls, loan, status, fully_paid_date):
        try:
            print("update status")
            if status in cls.LoanStatus:
                loan.status = status
                loan.fully_paid_date = fully_paid_date
                loan.save()
            else:
                print("Invalid Status")
        except cls.DoesNotExist:
            print("Loan not found")

    def __str__(self):
        return f"{self.client} - {str(self.loan_number)}"


class LoanAmortization(TimeStampedModel):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    term = models.IntegerField(null=True, blank=False)
    maturity_date = models.DateField(null=True, blank=True)
    principal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    running_balance = models.DecimalField(max_digits=10, null=True, decimal_places=2)
    fully_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.loan.client} - {self.loan.loan_number} - {self.maturity_date}"


class Payment(TimeStampedModel):
    class PaymentMethod(models.TextChoices):
        cash = (
            "cash",
            "Cash",
        )

    transaction = models.OneToOneField(
        Transaction, null=True, blank=True, on_delete=models.CASCADE
    )
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.cash
    )
    payment_ref = models.CharField(max_length=15, editable=False, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(max_length=50, null=True, blank=True)
    payment_date = models.DateTimeField(null=True, auto_now_add=True)

    def calculate_amortization_schedule(self):
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d")
        loan_amortization = LoanAmortization.objects.filter(loan=self.loan).order_by(
            "maturity_date"
        )
        amortization_due_date = loan_amortization.filter(
            maturity_date__gte=formatted_date
        )
        due_date = amortization_due_date.first().maturity_date.strftime("%Y-%m-%d")
        amortization = loan_amortization.filter(maturity_date__lte=due_date)
        total_principal_amount = amortization.aggregate(
            principal_amount=models.Sum("principal_amount")
        )["principal_amount"]
        total_interest_amount = amortization.aggregate(
            interest_amount=models.Sum("interest_amount")
        )["interest_amount"]
        result = {
            "interest_amount": amortization_due_date.first().interest_amount,
            "principal_amount": amortization_due_date.first().principal_amount,
            "total_principal_amount": total_principal_amount,
            "total_interest_amount": total_interest_amount,
        }
        return result

    def create_transaction(self):
        transaction_type = "or"
        to_pay_interest_amount = 0
        to_pay_principal_amount = 0
        transaction = Transaction.objects.create(
            transaction_no=self.transaction, transaction_type=transaction_type
        )

        result = self.calculate_amortization_schedule()

        to_pay_interest_amount = result["total_interest_amount"]
        to_pay_principal_amount = result["total_principal_amount"]

        remaining_balance_interest_amount = (
            to_pay_interest_amount - self.loan.total_paid_interest
        )
        remaining_balannce_principal_amount = (
            to_pay_principal_amount - self.loan.total_paid_principal
        )

        if remaining_balance_interest_amount < 1:
            remaining_balannce_principal_amount = self.amount

        if remaining_balannce_principal_amount < 1:
            remaining_balannce_principal_amount = result["principal_amount"]

        self.transaction = transaction

        # create debit entry for interest
        if remaining_balance_interest_amount > 0:
            TransactionEntry.objects.update_or_create(
                transaction=transaction,
                entry_type="d",
                ledger_account=self.loan.terms.ledger_account,
                defaults={"amount": remaining_balance_interest_amount},
            )

        TransactionEntry.objects.update_or_create(
            transaction=transaction,
            entry_type="d",
            ledger_account=self.loan.loan_product.ledger_account,
            defaults={"amount": remaining_balannce_principal_amount},
        )

        TransactionEntry.objects.update_or_create(
            transaction=transaction,
            entry_type="c",
            defaults={
                "ledger_account": LedgerAccount.objects.get(account_number=100001),
                "amount": self.amount,
            },
        )

    def update_loan_status(self):
        if self.loan.loan_amount <= self.loan.total_paid_principal:
            status = "fully_paid"
            fully_paid_date = self.payment_date
            self.loan.update_loan_status(self.loan, status, fully_paid_date)

    def save(self, *args, **kwargs):
        if not self.payment_ref:  # check if the instance is being created
            self.payment_ref = str(uuid.uuid4().hex)[:15].upper()
            self.create_transaction()

        super().save(*args, **kwargs)

        self.update_loan_status()

    def __str__(self):
        return self.payment_ref
