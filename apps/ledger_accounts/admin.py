from django.contrib import admin
from .models import LedgerAccount


# Register your models here.
@admin.register(LedgerAccount)
class LedgerAccountAdmin(admin.ModelAdmin):
    list = ["account_title"]
    readonly_fields = ["account_number"]
