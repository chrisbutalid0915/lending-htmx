from django.contrib import admin
from .models import Transaction, TransactionEntry

# Register your models here.


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list = ["*"]


@admin.register(TransactionEntry)
class TransactionEntryAdmin(admin.ModelAdmin):
    list = ["*"]
