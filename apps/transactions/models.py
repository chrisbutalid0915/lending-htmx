from django.db import models
from apps.ledger_accounts.models import LedgerAccount


# Create your models here.
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Transaction(TimeStampedModel):
    class TransactionType(models.TextChoices):
        official_receipt = "or", "Official Receipt"
        journal_voucher = "jv", "Journal Entry"
        cash_voucher = "cv", "Cash Voucher"

    transaction_type = models.CharField(
        max_length=25, null=True, choices=TransactionType.choices
    )
    transaction_no = models.IntegerField(unique=True)
    description = models.TextField(max_length=250, blank=True)

    def save(self, *args, **kwargs):
        if not self.transaction_no:
            last_transaction = Transaction.objects.order_by("-transaction_no").first()
            if last_transaction:
                self.transaction_no = last_transaction.transaction_no + 1
            else:
                self.transaction_no = 10000001
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.transaction_type.upper()}# - {self.transaction_no}"


class TransactionEntry(TimeStampedModel):
    class EntryType(models.TextChoices):
        debit = "d", "Debit"
        credit = "c", "Credit"

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    ledger_account = models.ForeignKey(
        LedgerAccount, on_delete=models.CASCADE, null=True
    )
    entry_type = models.CharField(max_length=1, choices=EntryType.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.transaction} - {self.entry_type.upper()} - {self.amount}"
