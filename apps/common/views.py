from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView


class IndexView(LoginRequiredMixin, ListView):
    login_url = "users:login"
    template_name = "index.html"

    redirect_field_name = "common:index"

    def get_queryset(self):
        return None
