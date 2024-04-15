from django.contrib import admin
from .models import Collector

# Register your models here.


@admin.register(Collector)
class CollectorAdmin(admin.ModelAdmin):
    list = ["full_name"]
