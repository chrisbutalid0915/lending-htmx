from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import HttpResponse, redirect, render
from django.views import View
from django.views.generic.list import ListView


class Login(LoginView):
    # login_url = "users:login"
    # template_name = "dashboard/dashboard.html"

    # redirect_field_name = "dashboard:dashboard"

    # def get_queryset(self):
    #     return None

    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]

        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            messages.success(request, "You have been logged in!")
            return redirect("dashboard:dashboard")
        else:
            messages.success(request, "Incorrect Username of Password.")
            return redirect("users:login")


class UserLogout(View):
    def get(self, request):
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect("users:login")
