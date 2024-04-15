from django.db import models


# Create your models here.
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LedgerAccount(TimeStampedModel):
    class LedgerType(models.TextChoices):
        Assets = "assets", "Assets"
        Liabilities = "liabilities", "Liabilities"
        Equity = "equity", "Equity"
        Income = "income", "Income"
        Expenses = "expenses", "Expenses"

    ledger_type = models.CharField(
        max_length=25, null=True, blank=False, choices=LedgerType.choices
    )
    account_title = models.CharField(max_length=50, null=True, blank=False, unique=True)
    account_number = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True)

    @classmethod
    def create_instance(cls, ledger_type, account_title):
        instance = cls(ledger_type=ledger_type, account_title=account_title)
        instance.save()
        return instance

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.increment_account_number()

        super().save(*args, **kwargs)

    def increment_account_number(self):
        ledger_dict = {
            "assets": 100000,
            "liabilities": 200000,
            "equity": 300000,
            "income": 400000,
            "expenses": 500000,
        }
        last_record = (
            LedgerAccount.objects.filter(ledger_type=self.ledger_type)
            .order_by("-account_number")
            .first()
        )
        ledger_format_number = ledger_dict[self.ledger_type]
        if last_record:
            new_account_number = last_record.account_number + 1
        else:
            new_account_number = ledger_format_number + 1
        return new_account_number

    def __str__(self):
        return f"{self.account_title} - {self.account_number}"
