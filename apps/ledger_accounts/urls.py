from django.urls import path
from .views import LedgerAccountInformation, ViewLedgerForm, AddLedgerForm, UpdateLedgerForm, ledger_page, add_ledger, update_legder

app_name = "ledger_accounts"

urlpatterns = [
    path("ledgers/", LedgerAccountInformation.as_view(), name="ledgers"),
    path("view-ledger/<int:pk>/", ViewLedgerForm.as_view(), name="view-ledger"),
    path(
        "add-ledger-form/", AddLedgerForm.as_view(), name="add-ledger-form"
    ),
    path(
        "update-ledger-form/<int:pk>/",
        UpdateLedgerForm.as_view(),
        name="update-ledger-form",
    ),
]

htmx_urlpatterns = [
    path("ledger-page/<int:page>", ledger_page, name="ledger-page"),
    path("add-ledger/", add_ledger, name="add-ledger"),
    path("update-ledger/<int:pk>/", update_legder, name="update-ledger"),
]

urlpatterns += htmx_urlpatterns
