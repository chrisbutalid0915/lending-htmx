from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    # path("", views.DashboardView.as_view(), name="dashboard"),
    path("login/", views.Login.as_view(), name="login"),
    path("logout/", views.UserLogout.as_view(), name="logout"),
]
