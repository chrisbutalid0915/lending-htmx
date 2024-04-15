from django.urls import path

from apps.dashboard.views import DashboardView

app_name = "common"

urlpatterns = [path("", DashboardView.as_view(), name="index")]
