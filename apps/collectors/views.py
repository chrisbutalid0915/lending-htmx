from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.conf import settings
from .models import Collector
from django.db.models.functions import Concat
from django.db.models import Value
from django.core.paginator import Paginator
from .forms import CollectorForm
from django.contrib import messages
from django.views.generic import FormView


# Create your views here.
class CollectorInformation(LoginRequiredMixin, ListView):
    template_name = "collector/collectors.html"
    model = Collector

    paginate_by = settings.PAGINATE_BY  # set number of records per page


class ViewCollectorForm(LoginRequiredMixin, FormView):
    def get(self, request, pk):
        print("view collector details")
        collector = Collector.objects.get(pk=pk)
        form = CollectorForm(request.POST or None, instance=collector)

        context = {
            "collector": collector,
            "forms": form,
        }

        return render(request, "collector/partials/collector-view.html", context)



class AddCollectorForm(LoginRequiredMixin, ListView):
    def get(self, request):
        print("collector add page")
        collector = {"is_active": True}
        form = CollectorForm(request.POST or None)
        context = {"form": form, "collector": collector}
        return render(request, "collector/partials/collector-add-form.html", context)


class UpdateCollectorForm(LoginRequiredMixin, FormView):
    def get(self, request, pk):
        print("load collector update page")
        collector = Collector.objects.get(pk=pk)
        form = CollectorForm(request.POST or None, instance=collector)

        collector = get_object_or_404(Collector, pk=pk)
        context = {"collector": collector, "form": form}

        return render(request, "collector/partials/collector-update-form.html", context)


def collector_page(request, page):
    print("get page")
    search_text = request.POST.get("search-collector")
    collectors = Collector.objects.filter(full_name__icontains=search_text).order_by(
        "-created_at"
    )

    # setup pagination
    p = Paginator(collectors, settings.PAGINATE_BY)
    collectors = p.get_page(page)

    total_records = p.count  # count total records

    context = {"collectors": collectors, "total_records": total_records}
    return render(request, "collector/partials/collector-list-elements.html", context)


def add_collector(request):
    print("add collector")
    form = CollectorForm(request.POST or None)
    # loan = request.POST.get("loan")
    # payment = request.POST.get("amount")

    # print(form)
    if form.is_valid():
        form.save()

        collectors = Collector.objects.all()
        total_records = collectors.count()  # count total records

        messages.success(request, "Record added...")
        context = {"collectors": collectors, "total_records": total_records}
        return render(request, "collector/partials/collector-list.html", context)
    form = CollectorForm(request.POST or None)
    context = {"forms": form}
    return render(request, "collector/partials/collector-add-form.html", context)


def update_collector(request, pk):
    print("update collector")
    collector = Collector.objects.get(pk=pk)
    form = CollectorForm(request.POST, request.FILES or None, instance=collector)
    if form.is_valid():
        form.save()
        context = {"forms": form, "collector": collector}
        messages.success(request, "Record updated...")
        return render(request, "collector/partials/collector-view-details.html", context)
    form = CollectorForm(request.POST or None, instance=collector)
    context = {"forms": form}
    return render(request, "collector/partials/collector-update-form.html", context)