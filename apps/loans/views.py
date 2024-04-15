from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.conf import settings
from .models import Loan, LoanProduct, Payment, LoanTerm, LoanAmortization
from django.db.models.functions import Concat
from django.db.models import Value
from django.core.paginator import Paginator
from .forms import LoanForm, LoanProductForm, PaymentForm
from .signals import pre_bulk_create_signal
from django.contrib import messages
from .utils import merge_terms, calculate_loan_interest
from django.views.generic import FormView
from django.shortcuts import render, get_object_or_404
from decimal import Decimal
from .services import generate_amortization_schedule


# Create your views here.
class LoanInformation(LoginRequiredMixin, ListView):
    template_name = "loan/loans.html"
    model = Loan

    paginate_by = settings.PAGINATE_BY  # set number of records per page


class ViewLoanForm(LoginRequiredMixin, FormView):
    def get(self, request, pk):
        print("view loan details")
        current_record = Loan.objects.get(pk=pk)
        form = LoanForm(request.POST or None, instance=current_record)

        amortization_schedule = generate_amortization_schedule(
            current_record
        )  # generate amortization schedule

        total_principal = current_record.loan_amount  # total loan amount
        total_interest = sum(
            [i.get("interest_amount", 0) for i in amortization_schedule]
        )  # total interest amount
        total = sum(
            [i.get("total", 0) for i in amortization_schedule]
        )  # total monthly payment

        loan = get_object_or_404(Loan, pk=pk)

        context = {
            "loan": loan,
            "forms": form,
            "amortization": amortization_schedule,
            "total_principal": total_principal,
            "total_interest": total_interest,
            "total": total,
        }

        return render(request, "loan/partials/loan-view.html", context)
    

class AddLoanForm(LoginRequiredMixin, ListView):
    def get(self, request):
        print("load loan add page")
        form = LoanForm(request.POST or None)

        context = {"forms": form, "search_client": '',  "client_id": ''}
        return render(request, "loan/partials/loan-add-form.html", context)


class UpdateLoanForm(LoginRequiredMixin, FormView):
    def get(self, request, pk):
        print("load loan update page")
        loan = get_object_or_404(Loan, pk=pk)
        # loan = Loan.objects.get(pk=pk)
        form = LoanForm(request.POST or None, instance=loan)
        search_client= loan.client
        

        print(search_client)
        context = {"loan": loan, "forms": form, "search_client": search_client, "client_id": search_client.id}

        return render(request, "loan/partials/loan-update-form.html", context)


class LoanProductInformation(LoginRequiredMixin, ListView):
    template_name = "loan_product/loan_products.html"
    model = LoanProduct

    paginate_by = settings.PAGINATE_BY  # set number of records per page


class ViewLoanProductForm(LoginRequiredMixin, FormView):
    def get(self, request, pk):
        print("view loan product details")
        loan_product = LoanProduct.objects.get(pk=pk)
        form = LoanProductForm(request.POST or None, instance=loan_product)

        context = {
            "loan_product": loan_product,
            "forms": form,
        }

        return render(request, "loan_product/partials/loan-product-view.html", context)


class AddLoanProductForm(LoginRequiredMixin, ListView):
    def get(self, request):
        print("load loan product add page")
        terms_months = LoanTerm.TermsMonths
        terms = []
        form = LoanProductForm(request.POST or None)
        context = {"forms": form, "terms_months": terms_months, "terms": terms}
        return render(
            request, "loan_product/partials/loan-product-add-form.html", context
        )


class UpdateLoanProductForm(LoginRequiredMixin, FormView):
    def get(self, request, pk):
        print("load loan product update page")
        current_record = LoanProduct.objects.get(pk=pk)
        form = LoanProductForm(request.POST or None, instance=current_record)

        loan_product = get_object_or_404(LoanProduct, pk=pk)
        context = {"loan_product": loan_product, "forms": form}

        return render(
            request, "loan_product/partials/loan-product-update-form.html", context
        )


class PaymentInformation(LoginRequiredMixin, ListView):
    template_name = "payment/payments.html"
    model = Payment

    paginate_by = settings.PAGINATE_BY  # set number of records per page


class ViewPaymentForm(LoginRequiredMixin, FormView):
    def get(self, request, pk):
        print("view payment details")
        payment = Payment.objects.get(pk=pk)
        form = PaymentForm(request.POST or None, instance=payment)

        context = {
            "payment": payment,
            "forms": form,
        }

        return render(request, "payment/partials/payment-view.html", context)


class AddPaymentForm(LoginRequiredMixin, ListView):
    def get(self, request):
        print("load payment add page")
        form = PaymentForm(request.POST or None)
        context = {"forms": form}
        return render(request, "payment/partials/payment-add-form.html", context)


class UpdatePaymentForm(LoginRequiredMixin, FormView):
    def get(self, request, pk):
        print("load payment update page")
        current_record = Payment.objects.get(pk=pk)
        form = PaymentForm(request.POST or None, instance=current_record)

        payment = get_object_or_404(Payment, pk=pk)
        context = {"payment": payment, "forms": form}

        return render(request, "payment/partials/payment-update-form.html", context)


def terms(request):
    print("terms")
    form = LoanForm(request.GET)
    context = {"forms": form}
    return render(request, "loan/partials/loan-terms.html", context)


def loan_page(request, page):
    print("get page loan")
    search_text = request.POST.get("search-loan")
    loans = Loan.objects.filter(loan_number__icontains=search_text).order_by(
        "-created_at"
    )

    # setup pagination
    p = Paginator(loans, settings.PAGINATE_BY)
    loans = p.get_page(page)
    # for l in loans:
    #     print(l.total_paid_interest)
    total_records = p.count  # count total records

    context = {"loans": loans, "total_records": total_records}
    return render(request, "loan/partials/loan-list-elements.html", context)


def calculate_interest_amount(request):
    print("calculate interest amount")
    term = LoanTerm.objects.get(pk=request.POST.get("terms"))
    loan_amount = request.POST.get("loan_amount")
    terms = term.terms
    interest_rate = term.interest_rate / 100
    interest_amount = 0
    if loan_amount:
        loan_amount = Decimal(loan_amount)
        interest_amount = calculate_loan_interest(interest_rate, terms, loan_amount)
    # print(interest_amount)
    context = {"interest_amount": interest_amount}
    return render(request, "loan/partials/loan-interest-amount.html", context)


def view_loan_amortization_schedule(request, pk):
    print("amortization schedule")
    current_record = Loan.objects.get(pk=pk)

    amortization_schedule = generate_amortization_schedule(
        current_record
    )  # generate amortization schedule

    total_principal = current_record.loan_amount  # total loan amount
    total_interest = sum(
        [i.get("interest_amount", 0) for i in amortization_schedule]
    )  # total interest amount
    total = sum(
        [i.get("total", 0) for i in amortization_schedule]
    )  # total monthly payment

    loan = get_object_or_404(Loan, pk=pk)

    context = {
        "loan": loan,
        "amortization": amortization_schedule,
        "total_principal": total_principal,
        "total_interest": total_interest,
        "total": total,
    }

    return render(
        request, "loan/partials/loan-view-amortization-schedule.html", context
    )


def add_loan(request):
    print("add loan")
    form = LoanForm(request.POST or None)
    if form.is_valid():
        form.save()

        loans = Loan.objects.all()
        total_records = loans.count()  # count total records

        messages.success(request, "Record added...")
        context = {"loans": loans, "total_records": total_records}
        return render(request, "loan/partials/loan-list.html", context)
    form = LoanForm(request.POST or None)
    context = {"forms": form}
    return render(request, "loan/partials/loan-fields.html", context)


def update_loan(request, pk):
    print("update loan")
    current_record = Loan.objects.get(pk=pk)
    form = LoanForm(request.POST, request.FILES or None, instance=current_record)

    if form.is_valid():
        if current_record.status == "pending":
            form.save()
            # loans = Loan.objects.all()
            # total_records = loans.count()  # count total records
            # context = {"loans": loans, "total_records": total_records}
            message = "Record updated..."
            # messages.success(request, "Record updated...")
            # return render(request, "loan/partials/loan-list.html", context)
        elif current_record.status == "approved":
            message = "Loan is already approved..."
        elif current_record.status == "cancelled":
            message = "Loan is already cancelled..."
        elif current_record.status == "released":
            message = "Loan is already released..."

        loans = Loan.objects.all()
        total_records = loans.count()  # count total records
        context = {"loans": loans, "total_records": total_records}
        messages.success(request, message)
        return render(request, "loan/partials/loan-list.html", context)

    form = LoanForm(request.POST or None, instance=current_record)
    context = {"forms": form}
    return render(request, "loan/partials/loan-fields.html", context)


def approve_loan(request, pk):
    print("approve loan")
    current_record = Loan.objects.get(pk=pk)

    message = ""
    
    if current_record.status == "pending":
        # loan_status = LoanStatus.objects.get(status_name="Approved")
        # if loan_status:
        current_record.status = "approved"
        current_record.save()
        # amortization_schedule = generate_amortization_schedule(current_record)
        # LoanAmortization.objects.bulk_create(
        #     amortization_schedule
        # )  # bulk create amortization schedule
        message = "Loan Approved..."
    elif current_record.status == "approved":
        message = "Loan is already approved..."
    elif current_record.status == "cancelled":
        message = "Loan is already cancelled..."
    elif current_record.status == "released":
        message = "Loan is already released..."
    else:
        message = "Invalid Error"
    loans = Loan.objects.all()
    total_records = loans.count()  # count total records

    # setup pagination
    p = Paginator(loans, settings.PAGINATE_BY)
    loans = p.get_page(1)

    messages.success(request, message)
    context = {"loans": loans, "total_records": total_records}
    return render(request, "loan/partials/loan-list.html", context)


def release_loan(request, pk):
    print("release loan")
    current_record = Loan.objects.get(pk=pk)

    message = ""

    if current_record.status == "pending":
        message = "Loan is still waiting to approved..."
    elif current_record.status == "approved":
        current_record.status = "released"
        current_record.save()
        amortization_schedule = []
        for i in generate_amortization_schedule(current_record):
            amortization_schedule.append(
                LoanAmortization(
                    loan=i["loan"],
                    term=i["term"],
                    maturity_date=i["maturity_date"],
                    principal_amount=i["principal_amount"],
                    interest_amount=i["interest_amount"],
                    total=i["total"],
                    running_balance=i["running_balance"],
                )
            )

        LoanAmortization.objects.bulk_create(
            amortization_schedule
        )  # bulk create amortization schedule
        message = "Loan Released..."
    elif current_record.status == "cancelled":
        message = "Loan is already cancelled..."
    elif current_record.status == "released":
        message = "Loan is already released..."
    else:
        message = "Invalid Error"
    loans = Loan.objects.all()
    total_records = loans.count()  # count total records

    # setup pagination
    p = Paginator(loans, settings.PAGINATE_BY)
    loans = p.get_page(1)

    messages.success(request, message)
    context = {"loans": loans, "total_records": total_records}
    return render(request, "loan/partials/loan-list.html", context)


def cancel_loan(request, pk):
    print("cancel loan")
    current_record = Loan.objects.get(pk=pk)
    message = ""
    
    if current_record.status == "pending":
        current_record.status = "cancelled"
        current_record.save()
        message = "Loan Cancelled..."
    elif current_record.status == "approved":
        message = "Loan is already approved..."
    elif current_record.status == "cancelled":
        message = "Loan is already cancelled..."
    elif current_record.status == "released":
        message = "Loan is already released..."
    else:
        message = "Invalid Error"
    loans = Loan.objects.all()
    total_records = loans.count()  # count total records

    # setup pagination
    p = Paginator(loans, settings.PAGINATE_BY)
    loans = p.get_page(1)

    messages.success(request, message)
    context = {"loans": loans, "total_records": total_records}
    return render(request, "loan/partials/loan-list.html", context)


def loan_product_page(request, page):
    print("get page loan product")
    search_text = request.POST.get("search-loan-product")
    loan_products = LoanProduct.objects.filter(
        loan_product__icontains=search_text
    ).order_by("-created_at")

    # setup pagination
    p = Paginator(loan_products, settings.PAGINATE_BY)
    loan_products = p.get_page(page)

    total_records = p.count  # count total records

    context = {"loan_products": loan_products, "total_records": total_records}
    return render(
        request, "loan_product/partials/loan-product-list-elements.html", context
    )


def add_loan_product(request):
    print("add loan product")
    form = LoanProductForm(request.POST or None)

    loan_product_name = request.POST.get("loan_product")
    terms = dict(request.POST)["terms"]
    interest_rate = dict(request.POST)["interest_rate"]
    status = dict(request.POST)["status"]
    # print(terms)
    # print(interest_rate)
    # print(status)
    if form.is_valid():
        form.save()
        current_product = LoanProduct.objects.get(loan_product=loan_product_name)
        product_terms = merge_terms(terms, interest_rate, status)
        # print(product_terms)

        # create product terms
        bulk_create_product_terms = []
        for product_term in product_terms:
            bulk_create_product_terms.append(
                LoanTerm(
                    loan_product=current_product,
                    terms=product_term["terms"],
                    interest_rate=product_term["interest_rate"],
                    status=product_term["status"],
                    ledger_account=None,
                )
            )

        # Before bulk_create auto create for ledger account
        pre_bulk_create_signal.send(sender=LoanTerm, objects=bulk_create_product_terms)

        LoanTerm.objects.bulk_create(bulk_create_product_terms)

        # # Post bulk_create auto create for ledger account
        # post_bulk_create_signal.send(sender=LoanTerm, objects=bulk_create_product_terms, created=True)

        loan_products = LoanProduct.objects.all()
        total_records = loan_products.count()  # count total records

        messages.success(request, "Record added...")
        context = {"loan_products": loan_products, "total_records": total_records}
        return render(request, "loan_product/partials/loan-product-list.html", context)
    terms_months = LoanTerm.TermsMonths
    terms = []
    form = LoanProductForm(request.POST or None)
    context = {"forms": form, "terms_months": terms_months, "terms": terms}
    return render(request, "loan_product/partials/loan-product-add-form.html", context)


def update_loan_product(request, pk):
    print("update loan product")
    loan_product = LoanProduct.objects.get(pk=pk)
    terms = dict(request.POST)["terms"]
    interest_rate = dict(request.POST)["interest_rate"]
    status = dict(request.POST)["status"]
    form = LoanProductForm(request.POST, request.FILES or None, instance=loan_product)

    if form.is_valid():
        form.save()
        loan_terms = LoanTerm.objects.filter(loan_product=loan_product)
        product_terms = merge_terms(terms, interest_rate, status)  # merge terms

        if loan_terms:
            # update product terms records
            for loan_term in loan_terms:
                result = [
                    product_term
                    for product_term in product_terms
                    if product_term["terms"] == loan_term.terms
                ]
                if result:
                    loan_term.interest_rate = result[0]["interest_rate"]
                    loan_term.status = result[0]["status"]

            # bulk update
            LoanTerm.objects.bulk_update(loan_terms, ["interest_rate", "status"])
        else:
            bulk_create_product_terms = []
            for product_term in product_terms:
                bulk_create_product_terms.append(
                    LoanTerm(
                        loan_product=loan_product,
                        terms=product_term["terms"],
                        interest_rate=product_term["interest_rate"],
                        status=product_term["status"],
                    )
                )

            # Before bulk_create auto create for ledger account
            pre_bulk_create_signal.send(
                sender=LoanTerm, objects=bulk_create_product_terms
            )

            LoanTerm.objects.bulk_create(bulk_create_product_terms)
        context = {"forms": form, "loan_product": loan_product}
        return render(
            request, "loan_product/partials/loan-product-view-details.html", context
        )
    form = LoanProductForm(request.POST or None, instance=loan_product)
    context = {"forms": form}
    return render(request, "loan_product/partials/loan-product-fields.html", context)


def add_loan_product_terms(request):
    print("get page loan product terms")
    terms_months = LoanTerm.TermsMonths
    terms = [terms.value for terms in terms_months]
    interest_rate = [0 for _ in terms_months]
    status = ["" for _ in terms_months]
    loan_terms = merge_terms(terms, interest_rate, status)
    # print(loan_terms)
    context = {"loan_terms": loan_terms, "terms": terms}
    return render(
        request, "loan_product/partials/loan-product-list-terms.html", context
    )


def payment_page(request, page):
    print("get page payment")
    search_text = request.POST.get("search-payment")
    payments = (
        Payment.objects.prefetch_related("loan")
        .filter(payment_ref__icontains=search_text)
        .order_by("-created_at")
    )

    # setup pagination
    p = Paginator(payments, settings.PAGINATE_BY)
    payments = p.get_page(page)

    total_records = p.count  # count total records

    context = {"payments": payments, "total_records": total_records}
    return render(request, "payment/partials/payment-list-elements.html", context)


def add_payment(request):
    print("add payment")
    form = PaymentForm(request.POST or None)
    # loan = request.POST.get("loan")
    # payment = request.POST.get("amount")

    # print(form)
    if form.is_valid():
        form.save()

        payments = Payment.objects.all()
        total_records = payments.count()  # count total records

        messages.success(request, "Record added...")
        context = {"payments": payments, "total_records": total_records}
        return render(request, "payment/partials/payment-list.html", context)
    form = PaymentForm(request.POST or None)
    context = {"forms": form}
    return render(request, "payment/partials/payment-add-form.html", context)


def update_payment(request, pk):
    print("update payment")
    current_record = Payment.objects.get(pk=pk)
    form = PaymentForm(request.POST, request.FILES or None, instance=current_record)
    if form.is_valid():
        form.save()
        payments = Payment.objects.all()
        total_records = payments.count()  # count total records
        context = {"payments": payments, "total_records": total_records}
        messages.success(request, "Record updated...")
        return render(request, "payment/partials/payment-list.html", context)
    form = PaymentForm(request.POST or None, instance=current_record)
    context = {"forms": form}
    return render(request, "payment/partials/payment-update-form.html", context)


def update_loan_product_terms(request, pk):
    print("get page loan product terms")
    terms_months = LoanTerm.TermsMonths

    current_record = LoanProduct.objects.get(pk=pk)
    loan_terms = LoanTerm.objects.filter(loan_product=current_record)

    terms_months = LoanTerm.TermsMonths
    terms = [terms.value for terms in terms_months]

    if not loan_terms:
        terms = [terms.value for terms in terms_months]
        interest_rate = [0 for _ in terms_months]
        status = ["" for _ in terms_months]
        loan_terms = merge_terms(terms, interest_rate, status)

    # print(loan_terms)
    context = {"loan_terms": loan_terms, "terms": terms}
    return render(
        request, "loan_product/partials/loan-product-list-terms.html", context
    )


def view_loan_product_terms(request, pk):
    print("get loan product terms")
    current_record = LoanProduct.objects.get(pk=pk)
    loan_terms = LoanTerm.objects.filter(loan_product=current_record, status=True)
    context = {"loan_terms": loan_terms}
    return render(request, "loan_product/partials/loan-product-terms.html", context)
