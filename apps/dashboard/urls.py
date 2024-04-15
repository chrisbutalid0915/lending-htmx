from django.urls import path
from .views import DashboardView, donut_chart_statistic, bar_chart_statistic, recent_loan_activity, recent_payment_activity, recent_client

app_name = "dashboard"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]


htmx_urlpatterns = [
    path("donut-chart/", donut_chart_statistic, name="donut-chart"),
    path("bar-chart/", bar_chart_statistic, name="bar-chart"),
    path("recent-loan/", recent_loan_activity, name="recent-loan"),
    path("recent-payment/", recent_payment_activity, name="recent-payment"),
    path("recent-client/", recent_client, name="recent-client"),
]

urlpatterns += htmx_urlpatterns