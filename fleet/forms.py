from datetime import datetime

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import (
    Company,
    Driver,
    Foreman,
    Region,
    StatusChoice,
    User,
    UserRole,
    Vehicle,
    VehicleTask,
)


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Kullanıcı Adı",
        widget=forms.TextInput(
            attrs={
                "class": "form-control login-input",
                "placeholder": "Kullanıcı adınız",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="Parola",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control login-input",
                "placeholder": "Parolanız",
                "autocomplete": "current-password",
            }
        ),
    )


class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Bölge Adı giriniz...",
                }
            )
        }


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Firma Adı giriniz...",
                }
            )
        }


class ForemanForm(forms.ModelForm):
    username = forms.CharField(
        label="Kullanıcı Adı",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Kullanıcı adı"}),
    )
    password = forms.CharField(
        label="Parola",
        required=False,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Parola (yeni kayıt için zorunlu)"}
        ),
    )
    full_name = forms.CharField(
        label="Adı Soyadı",
        max_length=160,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Formen Adı Soyadı"}
        ),
    )

    class Meta:
        model = Foreman
        fields = ["region", "status"]
        widgets = {
            "region": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "region": "Sorumlu Bölge",
            "status": "Durumu",
        }

    def __init__(self, *args, **kwargs):
        self.instance_obj = kwargs.get("instance")
        super().__init__(*args, **kwargs)
        self.fields["region"].empty_label = "----------"
        self.fields["status"].choices = StatusChoice.choices
        if self.instance_obj and self.instance_obj.pk:
            self.fields["username"].initial = self.instance_obj.user.username
            self.fields["full_name"].initial = self.instance_obj.full_name
            self.fields["password"].help_text = "Boş bırakırsanız parola değişmez."
        else:
            self.fields["password"].required = True
            self.fields["status"].initial = StatusChoice.ASIL

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        qs = User.objects.filter(username=username)
        if self.instance_obj and self.instance_obj.pk:
            qs = qs.exclude(pk=self.instance_obj.user_id)
        if qs.exists():
            raise ValidationError("Bu kullanıcı adı zaten kullanılıyor.")
        return username

    def clean_full_name(self):
        full_name = self.cleaned_data["full_name"].strip()
        parts = full_name.split(None, 1)
        if len(parts) < 1:
            raise ValidationError("Ad soyad giriniz.")
        return full_name

    def save(self, commit=True):
        full_name = self.cleaned_data["full_name"].strip()
        parts = full_name.split(None, 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
        status = self.cleaned_data["status"]
        username = self.cleaned_data["username"]
        password = self.cleaned_data.get("password")

        if self.instance_obj and self.instance_obj.pk:
            user = self.instance_obj.user
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.role = UserRole.FORMEN
            if password:
                user.set_password(password)
            user.save()
            foreman = self.instance_obj
            foreman.first_name = first_name
            foreman.last_name = last_name
            foreman.region = self.cleaned_data["region"]
            foreman.status = status
            if commit:
                foreman.save()
            return foreman

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=UserRole.FORMEN,
        )
        user.set_password(password)
        user.save()
        foreman = Foreman(
            user=user,
            first_name=first_name,
            last_name=last_name,
            region=self.cleaned_data["region"],
            status=status,
        )
        if commit:
            foreman.save()
        return foreman


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            "plate",
            "vehicle_type",
            "status",
            "company",
            "region",
            "primary_foreman",
            "backup_foreman",
        ]
        widgets = {
            "plate": forms.TextInput(attrs={"class": "form-control", "placeholder": "Plaka"}),
            "vehicle_type": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Araç Cinsi"}
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "company": forms.Select(attrs={"class": "form-select"}),
            "region": forms.Select(attrs={"class": "form-select"}),
            "primary_foreman": forms.Select(attrs={"class": "form-select"}),
            "backup_foreman": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("company", "region", "primary_foreman", "backup_foreman"):
            self.fields[name].empty_label = "----------"
        self.fields["backup_foreman"].required = False

    def clean(self):
        cleaned = super().clean()
        primary = cleaned.get("primary_foreman")
        backup = cleaned.get("backup_foreman")
        if primary and backup and primary.pk == backup.pk:
            self.add_error(
                "backup_foreman", "Asıl Formen ile Yedek Formen aynı kişi olamaz."
            )
        return cleaned


class DriverForm(forms.ModelForm):
    full_name = forms.CharField(
        label="Adı Soyadı",
        max_length=160,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Driver
        fields = ["duty", "status", "company", "assigned_vehicle"]
        widgets = {
            "duty": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Görevi (Örn: Greyder Op.)",
                }
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "company": forms.Select(attrs={"class": "form-select"}),
            "assigned_vehicle": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].empty_label = "----------"
        self.fields["assigned_vehicle"].empty_label = "----------"
        if self.instance and self.instance.pk:
            self.fields["full_name"].initial = self.instance.full_name

    def clean_full_name(self):
        full_name = self.cleaned_data["full_name"].strip()
        if not full_name:
            raise ValidationError("Ad soyad giriniz.")
        return full_name

    def save(self, commit=True):
        full_name = self.cleaned_data["full_name"].strip()
        parts = full_name.split(None, 1)
        driver = super().save(commit=False)
        driver.first_name = parts[0]
        driver.last_name = parts[1] if len(parts) > 1 else ""
        if driver.assigned_vehicle_id:
            driver.company = driver.assigned_vehicle.company
        if commit:
            driver.save()
        return driver


class VehicleTaskForm(forms.ModelForm):
    READONLY_MODEL_FIELDS = (
        "assigned_supervisor_name",
        "assigned_supervisor_title",
        "dispatching_supervisor_name",
        "dispatching_supervisor_title",
        "task_type",
        "destination",
        "engine_hours_km",
    )

    departure_local = forms.CharField(
        label="Çıkış",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control datetime-picker",
                "placeholder": "gg.aa.yyyy ss:dd",
                "autocomplete": "off",
                "inputmode": "none",
            }
        ),
    )
    arrival_local = forms.CharField(
        label="Giriş",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control datetime-picker",
                "placeholder": "gg.aa.yyyy ss:dd",
                "autocomplete": "off",
                "inputmode": "none",
            }
        ),
    )

    class Meta:
        model = VehicleTask
        fields = [
            "assigned_supervisor_name",
            "assigned_supervisor_title",
            "dispatching_supervisor_name",
            "dispatching_supervisor_title",
            "task_type",
            "destination",
            "vehicle",
            "driver",
            "engine_hours_km",
        ]
        widgets = {
            "assigned_supervisor_name": forms.TextInput(
                attrs={"class": "form-control readonly-field", "readonly": True, "tabindex": "-1"}
            ),
            "assigned_supervisor_title": forms.TextInput(
                attrs={"class": "form-control readonly-field", "readonly": True, "tabindex": "-1"}
            ),
            "dispatching_supervisor_name": forms.TextInput(
                attrs={"class": "form-control readonly-field", "readonly": True, "tabindex": "-1"}
            ),
            "dispatching_supervisor_title": forms.TextInput(
                attrs={"class": "form-control readonly-field", "readonly": True, "tabindex": "-1"}
            ),
            "task_type": forms.TextInput(
                attrs={"class": "form-control readonly-field", "readonly": True, "tabindex": "-1"}
            ),
            "destination": forms.TextInput(
                attrs={"class": "form-control readonly-field", "readonly": True, "tabindex": "-1"}
            ),
            "vehicle": forms.Select(attrs={"class": "form-select"}),
            "driver": forms.Select(attrs={"class": "form-select"}),
            "engine_hours_km": forms.TextInput(
                attrs={"class": "form-control readonly-field", "readonly": True, "tabindex": "-1"}
            ),
        }

    def __init__(self, *args, region=None, formen_profile=None, **kwargs):
        self.region = region
        self.formen_profile = formen_profile
        super().__init__(*args, **kwargs)
        for name in self.READONLY_MODEL_FIELDS:
            self.fields[name].required = False
            self.fields[name].disabled = True

        vehicles = Vehicle.objects.filter(region=region).select_related("company")
        self.fields["vehicle"].queryset = vehicles
        self.fields["vehicle"].empty_label = None
        self.fields["vehicle"].label_from_instance = (
            lambda v: f"{v.plate} - {v.vehicle_type} ({v.get_status_display()})"
        )
        vehicle_ids = list(vehicles.values_list("id", flat=True))
        drivers = Driver.objects.filter(
            assigned_vehicle_id__in=vehicle_ids
        ).select_related("assigned_vehicle")
        self.fields["driver"].queryset = drivers
        self.fields["driver"].label_from_instance = (
            lambda d: f"{d.full_name} ({d.duty}) - {d.get_status_display()}"
        )
        if self.instance and self.instance.pk:
            self.fields["departure_local"].initial = self._fmt(self.instance.departure_datetime)
            self.fields["arrival_local"].initial = self._fmt(self.instance.arrival_datetime)
        if not self.is_bound:
            if self.instance and self.instance.pk:
                self.fields["dispatching_supervisor_title"].initial = (
                    self.instance.dispatching_supervisor_title or "Formen"
                )
            else:
                self.fields["dispatching_supervisor_title"].initial = "Formen"
                if formen_profile:
                    self.fields["dispatching_supervisor_name"].initial = formen_profile.full_name

    @staticmethod
    def _fmt(dt):
        if not dt:
            return ""
        local = timezone.localtime(dt)
        return local.strftime("%d.%m.%Y %H:%M")

    @staticmethod
    def _parse_local(value):
        value = (value or "").strip()
        for fmt in ("%d.%m.%Y %H:%M", "%d.%m.%Y %H:%M:%S", "%Y-%m-%dT%H:%M"):
            try:
                naive = datetime.strptime(value, fmt)
                return timezone.make_aware(naive, timezone.get_current_timezone())
            except ValueError:
                continue
        raise ValidationError("Geçerli bir tarih/saat giriniz (örn: 10.09.2026 08:30).")

    def clean_departure_local(self):
        return self._parse_local(self.cleaned_data.get("departure_local"))

    def clean_arrival_local(self):
        return self._parse_local(self.cleaned_data.get("arrival_local"))

    def clean(self):
        cleaned = super().clean()
        departure = cleaned.get("departure_local")
        arrival = cleaned.get("arrival_local")
        vehicle = cleaned.get("vehicle")
        driver = cleaned.get("driver")

        if departure and arrival and arrival <= departure:
            self.add_error(
                "arrival_local",
                "Varış tarihi ve saati, çıkış tarihi ve saatinden sonra olmalıdır.",
            )

        if vehicle and self.region and vehicle.region_id != self.region.id:
            self.add_error("vehicle", "Bu araç sizin bölgenize ait değil.")

        if vehicle and driver and driver.assigned_vehicle_id != vehicle.id:
            self.add_error("driver", "Seçilen şoför bu araca zimmetli değil.")

        return cleaned

    def save(self, commit=True, created_by=None):
        # disabled alanlar POST ile değiştirilemez; yalnızca araç/şoför/tarih güncellenir
        if self.instance and self.instance.pk:
            task = VehicleTask.objects.get(pk=self.instance.pk)
        else:
            task = VehicleTask(
                assigned_supervisor_name="",
                assigned_supervisor_title="",
                task_type="",
                destination="",
                engine_hours_km="",
                dispatching_supervisor_title="Formen",
                dispatching_supervisor_name=(
                    self.formen_profile.full_name if self.formen_profile else ""
                ),
            )

        task.vehicle = self.cleaned_data["vehicle"]
        task.driver = self.cleaned_data["driver"]
        task.departure_datetime = self.cleaned_data["departure_local"]
        task.arrival_datetime = self.cleaned_data["arrival_local"]
        task.company = task.vehicle.company
        task.region = task.vehicle.region

        if not task.pk and created_by is not None:
            task.created_by = created_by

        if commit:
            task.save()
        return task
