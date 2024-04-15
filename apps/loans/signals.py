from django.dispatch import receiver
from django.db.models.signals import Signal
from .models import LoanTerm, LedgerAccount

# Define signals
pre_bulk_create_signal = Signal()
post_bulk_create_signal = Signal()


@receiver(pre_bulk_create_signal, sender=LoanTerm)
def pre_bulk_create_handler(sender, objects, **kwargs):
    ledger_type = "income"
    for object in objects:
        account_title = f"Interest - {object.loan_product} Terms {object.terms}"
        ledger_account = LedgerAccount.create_instance(ledger_type, account_title)
        object.ledger_account = ledger_account
    print("Pre bulk_create operation")


@receiver(post_bulk_create_signal, sender=LoanTerm)
def post_bulk_create_handler(sender, objects, created, **kwargs):
    # Your custom logic after bulk_create
    print("Post bulk_create operation")
