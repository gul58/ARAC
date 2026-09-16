from datetime import datetime, time

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .decorators import formen_required, get_formen_or_403, ihale_required
from .forms import (
    CompanyForm,
    DriverForm,
    ForemanForm,
    LoginForm,
    RegionForm,
    VehicleForm,
    VehicleTaskForm,
)
from .models import Company, Driver, Foreman, Region, StatusChoice, Vehicle, VehicleTask


class AppLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_ihale:
            return reverse("ihale_regions")
        return reverse("formen_home")


class AppLogoutView(LogoutView):
    next_page = reverse_lazy("login")


@login_required
def home(request):
    if request.user.is_ihale:
        return redirect("ihale_regions")
    if request.user.is_formen:
        return redirect("formen_home")
    messages.error(request, "Hesabınız için tanımlı bir rol bulunamadı.")
    return redirect("login")


# ---------- İhale: Bölgeler ----------


@ihale_required
def ihale_regions(request):
    form = RegionForm(request.POST or None)
    edit_id = request.GET.get("edit")
    edit_obj = None
    if edit_id:
        edit_obj = get_object_or_404(Region, pk=edit_id)
        form = RegionForm(request.POST or None, instance=edit_obj)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Bölge güncellendi." if edit_obj else "Bölge kaydedildi.",
            )
            return redirect("ihale_regions")
    regions = Region.objects.all()
    return render(
        request,
        "fleet/ihale/regions.html",
        {"form": form, "regions": regions, "edit_obj": edit_obj, "active_nav": "bolgeler"},
    )


@ihale_required
@require_POST
def ihale_region_delete(request, pk):
    region = get_object_or_404(Region, pk=pk)
    try:
        region.delete()
        messages.success(request, "Bölge silindi.")
    except Exception:
        messages.error(
            request,
            "Bu bölge kullanımda olduğu için silinemedi.",
        )
    return redirect("ihale_regions")


# ---------- İhale: Firmalar ----------


@ihale_required
def ihale_companies(request):
    form = CompanyForm(request.POST or None)
    edit_id = request.GET.get("edit")
    edit_obj = None
    if edit_id:
        edit_obj = get_object_or_404(Company, pk=edit_id)
        form = CompanyForm(request.POST or None, instance=edit_obj)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Firma güncellendi." if edit_obj else "Firma kaydedildi.",
            )
            return redirect("ihale_companies")
    companies = Company.objects.all()
    return render(
        request,
        "fleet/ihale/companies.html",
        {
            "form": form,
            "companies": companies,
            "edit_obj": edit_obj,
            "active_nav": "firmalar",
        },
    )


@ihale_required
@require_POST
def ihale_company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk)
    try:
        company.delete()
        messages.success(request, "Firma silindi.")
    except Exception:
        messages.error(request, "Bu firma kullanımda olduğu için silinemedi.")
    return redirect("ihale_companies")


# ---------- İhale: Formenler ----------


@ihale_required
def ihale_foremen(request):
    edit_id = request.GET.get("edit")
    edit_obj = None
    if edit_id:
        edit_obj = get_object_or_404(Foreman, pk=edit_id)
        form = ForemanForm(request.POST or None, instance=edit_obj)
    else:
        form = ForemanForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Formen güncellendi." if edit_obj else "Formen kaydedildi.",
            )
            return redirect("ihale_foremen")
    foremen = Foreman.objects.select_related("region", "user").all()
    return render(
        request,
        "fleet/ihale/foremen.html",
        {"form": form, "foremen": foremen, "edit_obj": edit_obj, "active_nav": "formenler"},
    )


@ihale_required
@require_POST
def ihale_foreman_delete(request, pk):
    foreman = get_object_or_404(Foreman, pk=pk)
    user = foreman.user
    try:
        foreman.delete()
        user.delete()
        messages.success(request, "Formen silindi.")
    except Exception:
        messages.error(request, "Bu formen kullanımda olduğu için silinemedi.")
    return redirect("ihale_foremen")


# ---------- İhale: Araçlar ----------


@ihale_required
def ihale_vehicles(request):
    edit_id = request.GET.get("edit")
    edit_obj = None
    if edit_id:
        edit_obj = get_object_or_404(Vehicle, pk=edit_id)
        form = VehicleForm(request.POST or None, instance=edit_obj)
    else:
        form = VehicleForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Araç güncellendi." if edit_obj else "Araç kaydedildi.",
            )
            return redirect("ihale_vehicles")
    vehicles = Vehicle.objects.select_related(
        "company", "region", "primary_foreman", "backup_foreman"
    ).all()
    return render(
        request,
        "fleet/ihale/vehicles.html",
        {"form": form, "vehicles": vehicles, "edit_obj": edit_obj, "active_nav": "araclar"},
    )


@ihale_required
@require_POST
def ihale_vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    try:
        vehicle.delete()
        messages.success(request, "Araç silindi.")
    except Exception:
        messages.error(request, "Bu araç kullanımda olduğu için silinemedi.")
    return redirect("ihale_vehicles")


# ---------- İhale: Şoförler ----------


@ihale_required
def ihale_drivers(request):
    edit_id = request.GET.get("edit")
    edit_obj = None
    if edit_id:
        edit_obj = get_object_or_404(Driver, pk=edit_id)
        form = DriverForm(request.POST or None, instance=edit_obj)
    else:
        form = DriverForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Şoför güncellendi." if edit_obj else "Şoför kaydedildi.",
            )
            return redirect("ihale_drivers")
    drivers = Driver.objects.select_related("company", "assigned_vehicle").all()
    return render(
        request,
        "fleet/ihale/drivers.html",
        {"form": form, "drivers": drivers, "edit_obj": edit_obj, "active_nav": "soforler"},
    )


@ihale_required
@require_POST
def ihale_driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    try:
        driver.delete()
        messages.success(request, "Şoför silindi.")
    except Exception:
        messages.error(request, "Bu şoför kullanımda olduğu için silinemedi.")
    return redirect("ihale_drivers")


@ihale_required
def ihale_report(request):
    """İhale: tarih aralığı + bölge/firma/formen/şoför filtreli görev emri listesi."""
    today = timezone.localdate()
    start_raw = request.GET.get("start_date") or today.replace(day=1).isoformat()
    end_raw = request.GET.get("end_date") or today.isoformat()
    selected_region = request.GET.get("region", "")
    selected_company = request.GET.get("company", "")
    selected_foreman = request.GET.get("foreman", "")
    selected_driver = request.GET.get("driver", "")
    searched = "start_date" in request.GET or "end_date" in request.GET
    error = ""
    tasks = []

    if searched:
        try:
            start = datetime.strptime(start_raw, "%Y-%m-%d").date()
            end = datetime.strptime(end_raw, "%Y-%m-%d").date()
            if end < start:
                raise ValueError("Son tarih, ilk tarihten önce olamaz.")
            start_dt = timezone.make_aware(datetime.combine(start, time.min))
            end_dt = timezone.make_aware(datetime.combine(end, time.max))
            qs = (
                VehicleTask.objects.filter(
                    departure_datetime__gte=start_dt,
                    departure_datetime__lte=end_dt,
                )
                .select_related(
                    "region",
                    "company",
                    "vehicle",
                    "driver",
                    "created_by",
                    "created_by__formen_profile",
                )
                .order_by("region__name", "departure_datetime", "id")
            )
            if selected_region:
                qs = qs.filter(region_id=selected_region)
            if selected_company:
                qs = qs.filter(company_id=selected_company)
            if selected_foreman:
                foreman = Foreman.objects.filter(pk=selected_foreman).first()
                if foreman:
                    qs = qs.filter(created_by_id=foreman.user_id)
                else:
                    qs = qs.none()
            if selected_driver:
                qs = qs.filter(driver_id=selected_driver)
            tasks = list(qs)
        except ValueError as exc:
            error = str(exc)

    return render(
        request,
        "fleet/ihale/report.html",
        {
            "active_nav": "rapor",
            "regions": Region.objects.all(),
            "companies": Company.objects.all(),
            "foremen": Foreman.objects.select_related("region", "user").all(),
            "drivers": Driver.objects.all(),
            "start_date": start_raw,
            "end_date": end_raw,
            "selected_region": selected_region,
            "selected_company": selected_company,
            "selected_foreman": selected_foreman,
            "selected_driver": selected_driver,
            "tasks": tasks,
            "searched": searched,
            "error": error,
        },
    )


# ---------- Formen ----------


@formen_required
def formen_home(request):
    get_formen_or_403(request.user)
    return render(request, "fleet/formen/home.html", {"active_nav": "home"})


def _task_queryset_for_formen(user):
    profile = get_formen_or_403(user)
    return VehicleTask.objects.filter(region_id=profile.region_id).select_related(
        "company", "vehicle", "driver", "region"
    )


def _get_task_for_formen(user, pk):
    profile = get_formen_or_403(user)
    try:
        return VehicleTask.objects.select_related(
            "company", "vehicle", "driver", "region"
        ).get(pk=pk, region_id=profile.region_id)
    except VehicleTask.DoesNotExist:
        raise Http404("Görev emri bulunamadı veya yetkiniz yok.")


@formen_required
def formen_task_create(request):
    profile = get_formen_or_403(request.user)
    form = VehicleTaskForm(
        request.POST or None, region=profile.region, formen_profile=profile
    )
    if request.method == "POST":
        if form.is_valid():
            form.save(created_by=request.user)
            messages.success(request, "Görev emri başarıyla kaydedildi.")
            return redirect("formen_task_list")
    last = VehicleTask.objects.order_by("-id").first()
    next_seq = (last.id if last else 0) + 1
    next_number = Region.format_task_number(profile.region, next_seq)
    return render(
        request,
        "fleet/formen/task_form.html",
        {
            "form": form,
            "profile": profile,
            "task": None,
            "task_number": next_number,
            "active_nav": "kaydet",
            "page_title": "Görev Emri Kayıt",
        },
    )


@formen_required
def formen_task_list(request):
    tasks = _task_queryset_for_formen(request.user)
    return render(
        request,
        "fleet/formen/task_list.html",
        {"tasks": tasks, "active_nav": "liste"},
    )


@formen_required
def formen_task_edit(request, pk):
    profile = get_formen_or_403(request.user)
    task = _get_task_for_formen(request.user, pk)
    form = VehicleTaskForm(
        request.POST or None,
        instance=task,
        region=profile.region,
        formen_profile=profile,
    )
    if request.method == "POST":
        if form.is_valid():
            form.save(created_by=task.created_by)
            messages.success(request, "Görev emri güncellendi.")
            return redirect("formen_task_list")
    return render(
        request,
        "fleet/formen/task_form.html",
        {
            "form": form,
            "profile": profile,
            "task": task,
            "task_number": task.display_number,
            "active_nav": "liste",
            "page_title": "Görev Emri Düzenle",
        },
    )


@formen_required
@require_POST
def formen_task_delete(request, pk):
    task = _get_task_for_formen(request.user, pk)
    task.delete()
    messages.success(request, "Görev emri silindi.")
    return redirect("formen_task_list")


@formen_required
def formen_report(request):
    """Tarih aralığına göre görev emri formlarını PDF olarak dışa aktarır."""
    profile = get_formen_or_403(request.user)
    today = timezone.localdate()
    start_date = request.POST.get("start_date") or request.GET.get("start_date") or today.replace(day=1).isoformat()
    end_date = request.POST.get("end_date") or request.GET.get("end_date") or today.isoformat()
    error = ""
    preview_tasks = None
    tasks = VehicleTask.objects.none()

    def parse_dates():
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            raise ValueError("Geçerli ilk ve son tarih seçiniz.")
        if end < start:
            raise ValueError("Son tarih, ilk tarihten önce olamaz.")
        return start, end

    def queryset_for(start, end):
        start_dt = timezone.make_aware(datetime.combine(start, time.min))
        end_dt = timezone.make_aware(datetime.combine(end, time.max))
        return (
            VehicleTask.objects.filter(
                region_id=profile.region_id,
                departure_datetime__gte=start_dt,
                departure_datetime__lte=end_dt,
            )
            .select_related("company", "vehicle", "driver", "region")
            .order_by("departure_datetime", "id")
        )

    if request.method == "POST":
        try:
            start, end = parse_dates()
            tasks = queryset_for(start, end)
            if request.POST.get("export"):
                if not tasks.exists():
                    error = "Seçilen tarih aralığında görev emri bulunamadı."
                else:
                    from .pdf import build_tasks_pdf

                    pdf_buffer = build_tasks_pdf(tasks, region_name=profile.region.name)
                    filename = f"gorev-emri-{start.isoformat()}_{end.isoformat()}.pdf"
                    response = HttpResponse(pdf_buffer.getvalue(), content_type="application/pdf")
                    response["Content-Disposition"] = f'attachment; filename="{filename}"'
                    return response
            # preview
            preview_tasks = list(tasks)
        except ValueError as exc:
            error = str(exc)

    return render(
        request,
        "fleet/formen/report.html",
        {
            "profile": profile,
            "active_nav": "rapor",
            "start_date": start_date,
            "end_date": end_date,
            "error": error,
            "preview_tasks": preview_tasks,
            "task_count": len(preview_tasks) if preview_tasks is not None else 0,
        },
    )


@formen_required
@require_GET
def formen_vehicle_drivers(request, vehicle_id):
    """Araç seçildiğinde şoför listesini JSON olarak döner."""
    profile = get_formen_or_403(request.user)
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id, region_id=profile.region_id)
    drivers = Driver.objects.filter(assigned_vehicle=vehicle).order_by(
        "status", "first_name"
    )
    data = {
        "company": vehicle.company.name,
        "vehicle_label": f"{vehicle.plate} - {vehicle.vehicle_type} ({vehicle.get_status_display()})",
        "drivers": [
            {
                "id": d.id,
                "label": f"{d.full_name} ({d.duty}) - {d.get_status_display()}",
                "is_primary": d.status == StatusChoice.ASIL,
            }
            for d in drivers
        ],
    }
    return JsonResponse(data)
