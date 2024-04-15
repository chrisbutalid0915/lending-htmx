from django.urls import path
from .views import (
    LoanInformation,
    ViewLoanForm,
    AddLoanForm,
    UpdateLoanForm,
    LoanProductInformation,
    ViewLoanProductForm,
    AddLoanProductForm,
    UpdateLoanProductForm,
    PaymentInformation,
    ViewPaymentForm,
    AddPaymentForm,
    UpdatePaymentForm,
    terms,
    loan_page,
    calculate_interest_amount,
    view_loan_amortization_schedule,
    add_loan,
    update_loan,
    approve_loan,
    release_loan,
    cancel_loan,
    loan_product_page,
    payment_page,
    add_payment,
    update_payment,
    add_loan_product,
    update_loan_product,
    add_loan_product_terms,
    update_loan_product_terms,
    view_loan_product_terms,
)

app_name = "loans"

urlpatterns = [
    path("loans/", LoanInformation.as_view(), name="loans"),
    path(
        "view-loan-form/<int:pk>/",
        ViewLoanForm.as_view(),
        name="view-loan-form",
    ),
    path("add-loan-form/", AddLoanForm.as_view(), name="add-loan-form"),
    path(
        "update-loan-form/<int:pk>/",
        UpdateLoanForm.as_view(),
        name="update-loan-form",
    ),
    path("loan-products/", LoanProductInformation.as_view(), name="loan-products"),
    path(
        "view-loan-product/<int:pk>/",
        ViewLoanProductForm.as_view(),
        name="view-loan-product",
    ),
    path(
        "add-loan-product-form/",
        AddLoanProductForm.as_view(),
        name="add-loan-product-form",
    ),
    path(
        "update-loan-product-form/<int:pk>/",
        UpdateLoanProductForm.as_view(),
        name="update-loan-product-form",
    ),
    
    path("payments/", PaymentInformation.as_view(), name="payments"),
    path("view-payment/<int:pk>/", ViewPaymentForm.as_view(), name="view-payment"),
    path(
        "add-payment-form/",
        AddPaymentForm.as_view(),
        name="add-payment-form",
    ),
    path(
        "update-payment-form/<int:pk>/",
        UpdatePaymentForm.as_view(),
        name="update-payment-form",
    ),
]

htmx_urlpatterns = [
    path("terms/", terms, name="terms"),
    path("loan-page/<int:page>", loan_page, name="loan-page"),
    path("add-loan/", add_loan, name="add-loan"),
    path("update-loan/<int:pk>/", update_loan, name="update-loan"),
    path("approve-loan/<int:pk>/", approve_loan, name="approve-loan"),
    path("release-loan/<int:pk>/", release_loan, name="release-loan"),
    path("cancel-loan/<int:pk>/", cancel_loan, name="cancel-loan"),
    path(
        "calculate-interest-amount/",
        calculate_interest_amount,
        name="calculate-interest-amount",
    ),
    path(
        "view-loan-amortization-schedule/<int:pk>/",
        view_loan_amortization_schedule,
        name="view-loan-amortization-schedule",
    ),
    path("loan-product-page/<int:page>", loan_product_page, name="loan-product-page"),
    path("add-loan-product/", add_loan_product, name="add-loan-product"),
    path(
        "update-loan-product/<int:pk>/", update_loan_product, name="update-loan-product"
    ),
    path(
        "add-loan-product-terms/", add_loan_product_terms, name="add-loan-product-terms"
    ),
    path(
        "update-loan-product-terms/<int:pk>/",
        update_loan_product_terms,
        name="update-loan-product-terms",
    ),
    path("payment-page/<int:page>", payment_page, name="payment-page"),
    path("add-payment/", add_payment, name="add-payment"),
    path(
        "update-payment/<int:pk>/", update_payment, name="update-payment"
    ),
    path(
        "view-loan-product-terms/<int:pk>",
        view_loan_product_terms,
        name="view-loan-product-terms",
    ),
]

urlpatterns += htmx_urlpatterns
