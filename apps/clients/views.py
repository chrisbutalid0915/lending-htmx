from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.conf import settings
from .models import Client
from django.db.models.functions import Concat
from django.db.models import Value
from django.core.paginator import Paginator
from django.views.generic import FormView
from .forms import ClientForm
from django.contrib import messages
from django.shortcuts import get_object_or_404, render


# Create your views here.
class ClientInformation(LoginRequiredMixin, ListView):
    template_name = "client/clients.html"
    model = Client

    paginate_by = settings.PAGINATE_BY  # set number of records per page


class ViewClientForm(LoginRequiredMixin, FormView):
    def get(self, request, pk):
        print("view client details")
        client = Client.objects.get(pk=pk)
        form = ClientForm(request.POST or None, instance=client)

        context = {
            "client": client,
            "forms": form,
        }

        return render(request, "client/partials/client-view.html", context)


class AddClientForm(LoginRequiredMixin, ListView):
    def get(self, request):
        print("load client add page")
        form = ClientForm(request.POST or None)
        client = {"photo": None}
        context = {"client": client, "forms": form}
        return render(request, "client/partials/client-add-form.html", context)


class ViewClientForm(LoginRequiredMixin, FormView):
    def get(self, request, pk):
        print("view client details")
        client = Client.objects.get(pk=pk)
        form = ClientForm(request.POST or None, instance=client)

        context = {
            "client": client,
            "forms": form,
        }

        return render(request, "client/partials/client-view.html", context)


class UpdateClientForm(LoginRequiredMixin, FormView):
    def get(self, request, pk):
        print("load client update page")
        current_record = Client.objects.get(id=pk)
        form = ClientForm(request.POST or None, instance=current_record)

        client = get_object_or_404(Client, pk=pk)
        context = {"client": client, "forms": form}

        return render(request, "client/partials/client-update-form.html", context)


def search_client(request):
    print("search")
    search_text = request.POST.get("search-client")
    annotated_objects = Client.objects.annotate(
        fullname=Concat(
            'first_name',
            Value(' '),  # Separator
            'middle_name',
            Value(' '),  # Separator
            'last_name'
        )
    )
    
    clients = annotated_objects.filter(fullname__icontains=search_text)

    total_records = clients.count()  # count total records

    context = {"clients": clients, "total_records": total_records}
    return render(request, "client/partials/combobox-client-search.html", context)


def client_page(request, page):
    print("get page")
    search_text = request.POST.get("search-client")
    print(search_text)
    annotated_objects = Client.objects.annotate(
        fullname=Concat(
            "first_name",
            Value(" "),  # Separator
            "middle_name",
            Value(" "),  # Separator
            "last_name",
        )
    )

    clients = annotated_objects.filter(fullname__icontains=search_text).order_by(
        "-created_at"
    )

    # setup pagination
    p = Paginator(clients, settings.PAGINATE_BY)
    clients = p.get_page(page)

    total_records = p.count  # count total records

    context = {"clients": clients, "total_records": total_records}
    return render(request, "client/partials/client-list-elements.html", context)


def add_client(request):
    print("add client")
    form = ClientForm(request.POST, request.FILES or None)
    if form.is_valid():
        form.save()
        clients = Client.objects.all()
        context = {"clients": clients}
        messages.success(request, "Record added...")
        return render(request, "client/partials/client-list.html", context)
    form = ClientForm(request.POST or None)
    context = {"forms": form}
    return render(request, "client/partials/client-fields.html", context)


def update_client(request, pk):
    print("update client")
    current_record = Client.objects.get(id=pk)
    form = ClientForm(request.POST, request.FILES or None, instance=current_record)
    if form.is_valid():
        form.save()
        # clients = Client.objects.all()
        context = {"forms": form, "client": current_record}
        messages.success(request, "Record updated...")
        return render(request, "client/partials/client-view-details.html", context)
    form = ClientForm(request.POST or None, instance=current_record)
    context = {"forms": form, "client": current_record}
    return render(request, "client/partials/client-fields.html", context)