from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.conf import settings
from django.contrib import messages
from .models import LedgerAccount
from django.db.models.functions import Concat
from django.db.models import Value
from django.core.paginator import Paginator
from django.views.generic import FormView
from .forms import LedgerAccountForm


# Create your views here.
class LedgerAccountInformation(LoginRequiredMixin, ListView):
    template_name = "ledger/ledger.html"
    model = LedgerAccount

    paginate_by = settings.PAGINATE_BY  # set number of records per page


class ViewLedgerForm(LoginRequiredMixin, FormView):
    def get(self, request, pk):
        print("view ledger details")
        ledger = LedgerAccount.objects.get(pk=pk)
        form = LedgerAccountForm(request.POST or None, instance=ledger)

        context = {
            "ledger": ledger,
            "forms": form,
        }

        return render(request, "ledger/partials/ledger-view.html", context)


class AddLedgerForm(LoginRequiredMixin, ListView):
    def get(self, request):
        print("load ledger add page")
        form = LedgerAccountForm(request.POST or None)
        ledger = {"status": True}
        context = {"forms": form, "ledger": ledger}
        return render(request, "ledger/partials/ledger-add-form.html", context)


class UpdateLedgerForm(LoginRequiredMixin, FormView):
    def get(self, request, pk):
        print("load ledger update page")
        current_record = LedgerAccount.objects.get(pk=pk)
        form = LedgerAccountForm(request.POST or None, instance=current_record)

        ledger = get_object_or_404(LedgerAccount, pk=pk)
        context = {"ledger": ledger, "forms": form}

        return render(request, "ledger/partials/ledger-update-form.html", context)


def ledger_page(request, page):
    print("get page ledger")
    search_text = request.POST.get("search-ledger")
    ledgers = LedgerAccount.objects.filter(
        account_title__icontains=search_text
    ).order_by("-created_at")

    # setup pagination
    p = Paginator(ledgers, settings.PAGINATE_BY)
    ledgers = p.get_page(page)

    total_records = p.count  # count total records

    context = {"ledgers": ledgers, "total_records": total_records}
    return render(request, "ledger/partials/ledger-list-elements.html", context)


def add_ledger(request):
    print("add ledger")
    form = LedgerAccountForm(request.POST or None)
    # print(form)
    if form.is_valid():
        form.save()

        ledgers = LedgerAccount.objects.all()
        total_records = ledgers.count()  # count total records

        messages.success(request, "Record added...")
        context = {"ledgers": ledgers, "total_records": total_records}
        return render(request, "ledger/partials/ledger-list.html", context)
    form = LedgerAccountForm(request.POST or None)
    context = {"forms": form}
    return render(request, "ledger/partials/ledger-fields.html", context)



def update_legder(request, pk):
    print("update ledger")
    ledger = LedgerAccount.objects.get(pk=pk)
    form = LedgerAccountForm(request.POST, request.FILES or None, instance=ledger)
    if form.is_valid():
        form.save()
        context = {"forms": form, "ledger": ledger}
        messages.success(request, "Record updated...")
        return render(request, "ledger/partials/ledger-view-details.html", context)
    form = LedgerAccountForm(request.POST or None, instance=ledger)
    context = {"forms": form}
    return render(request, "ledger/partials/ledger-fields.html", context)
