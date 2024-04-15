from django.urls import path
from .views import (
    ClientInformation,
    AddClientForm,
    ViewClientForm,
    UpdateClientForm,
    search_client,
    client_page,
    add_client,
    update_client,
)

app_name = "clients"

urlpatterns = [
    path("clients/", ClientInformation.as_view(), name="clients"),
    path("add-client-form/", AddClientForm.as_view(), name="add-client-form"),
    path("view-client/<int:pk>/", ViewClientForm.as_view(), name="view-client"),
    path(
        "update-client-form/<int:pk>/",
        UpdateClientForm.as_view(),
        name="update-client-form",
    ),
]

htmx_urlpatterns = [
    path("search-client/", search_client, name="search-client"),
    path("client-page/<int:page>", client_page, name="page-client"),
    path("add-client/", add_client, name="add-client"),
    path("update-client/<int:pk>/", update_client, name="update-client"),
    
]

urlpatterns += htmx_urlpatterns
