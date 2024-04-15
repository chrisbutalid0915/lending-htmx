from django.urls import path
from .views import CollectorInformation, ViewCollectorForm, AddCollectorForm, UpdateCollectorForm, collector_page, add_collector, update_collector

app_name = "collectors"

urlpatterns = [
    path("collectors/", CollectorInformation.as_view(), name="collectors"),
    path("view-collector/<int:pk>/", ViewCollectorForm.as_view(), name="view-collector"),
    path(
        "add-collector-form/",
        AddCollectorForm.as_view(),
        name="add-collector-form",
    ),
    path(
        "update-collector-form/<int:pk>/",
        UpdateCollectorForm.as_view(),
        name="update-collector-form",
    ),
]


htmx_urlpatterns = [
    path("collector-page/<int:page>", collector_page, name="page-collector"),
    
    path("add-collector/", add_collector, name="add-collector"),
    path(
        "update-collector/<int:pk>/", update_collector, name="update-collector"
    ),
]

urlpatterns += htmx_urlpatterns
