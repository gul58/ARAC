from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class UserRole(models.TextChoices):
    IHALE = "ihale", "İhale"
    FORMEN = "formen", "Formen"


class StatusChoice(models.TextChoices):
    ASIL = "asil", "Asıl"
    YEDEK = "yedek", "Yedek"


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.FORMEN,
        verbose_name="Rol",
    )

    class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"

    @property
    def is_ihale(self):
        return self.role == UserRole.IHALE or self.is_superuser

    @property
    def is_formen(self):
        return self.role == UserRole.FORMEN and not self.is_superuser

    def get_formen_profile(self):
        return getattr(self, "formen_profile", None)


class Region(models.Model):
    # Görev emri numarası için bölge kodları
    CODE_MAP = {
        "DERİNCE": "DRN",
        "DERINCE": "DRN",
        "BAŞİSKELE": "BSS",
        "BASISKELE": "BSS",
        "GÖLCÜK": "GLC",
        "GOLCUK": "GLC",
        "KARTEPE": "KRT",
        "KÖRFEZ": "KRF",
        "KORFEZ": "KRF",
        "KARAMÜRSEL": "KRM",
        "KARAMURSEL": "KRM",
        "KANDIRA": "KND",
        "İZMİT": "ZMT",
        "IZMIT": "ZMT",
        "DİLOVASI": "DLV",
        "DILOVASI": "DLV",
        "GEBZE": "GBZ",
        "ÇAYIROVA": "CYR",
        "CAYIROVA": "CYR",
        "DARICA": "DRC",
    }

    STANDARD_REGIONS = (
        ("Derince", "DRN"),
        ("Başiskele", "BSS"),
        ("Gölcük", "GLC"),
        ("Kartepe", "KRT"),
        ("Körfez", "KRF"),
        ("Karamürsel", "KRM"),
        ("Kandıra", "KND"),
        ("İzmit", "ZMT"),
        ("Dilovası", "DLV"),
        ("Gebze", "GBZ"),
        ("Çayırova", "CYR"),
        ("Darıca", "DRC"),
    )

    name = models.CharField(max_length=100, unique=True, verbose_name="Bölge Adı")
    code = models.CharField(
        max_length=10,
        blank=True,
        default="",
        verbose_name="Kod",
        help_text="Görev emri numarası için kısaltma (örn: DRN)",
    )

    class Meta:
        verbose_name = "Bölge"
        verbose_name_plural = "Bölgeler"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            key = self.name.strip().upper()
            self.code = self.CODE_MAP.get(key, "")
        super().save(*args, **kwargs)

    @classmethod
    def format_task_number(cls, region, sequence):
        code = ""
        if region is not None:
            code = (region.code or "").strip().upper()
            if not code:
                code = cls.CODE_MAP.get(region.name.strip().upper(), "???")
        else:
            code = "???"
        return f"{code} - {int(sequence):08d}"


class Company(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Firma Adı")

    class Meta:
        verbose_name = "Firma"
        verbose_name_plural = "Firmalar"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Foreman(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="formen_profile",
        verbose_name="Kullanıcı",
    )
    first_name = models.CharField(max_length=80, verbose_name="Ad")
    last_name = models.CharField(max_length=80, verbose_name="Soyad")
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="foremen",
        verbose_name="Sorumlu Bölge",
    )
    status = models.CharField(
        max_length=10,
        choices=StatusChoice.choices,
        default=StatusChoice.ASIL,
        verbose_name="Durum",
    )

    class Meta:
        verbose_name = "Formen"
        verbose_name_plural = "Formenler"
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return self.display_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def display_name(self):
        # Ekranlarda kullanıcı adı veya ad soyad
        return self.user.username if self.user_id else self.full_name


class Vehicle(models.Model):
    plate = models.CharField(max_length=20, unique=True, verbose_name="Plaka")
    vehicle_type = models.CharField(max_length=80, verbose_name="Araç Tipi")
    status = models.CharField(
        max_length=10,
        choices=StatusChoice.choices,
        default=StatusChoice.ASIL,
        verbose_name="Durum",
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="vehicles",
        verbose_name="Firma",
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="vehicles",
        verbose_name="Bölge",
    )
    primary_foreman = models.ForeignKey(
        Foreman,
        on_delete=models.PROTECT,
        related_name="primary_vehicles",
        verbose_name="Asıl Formen",
    )
    backup_foreman = models.ForeignKey(
        Foreman,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="backup_vehicles",
        verbose_name="Yedek Formen",
    )

    class Meta:
        verbose_name = "Araç"
        verbose_name_plural = "Araçlar"
        ordering = ["plate"]

    def __str__(self):
        return f"{self.plate} ({self.vehicle_type})"

    def clean(self):
        if self.backup_foreman_id and self.primary_foreman_id:
            if self.backup_foreman_id == self.primary_foreman_id:
                raise ValidationError(
                    {"backup_foreman": "Asıl Formen ile Yedek Formen aynı kişi olamaz."}
                )


class Driver(models.Model):
    first_name = models.CharField(max_length=80, verbose_name="Ad")
    last_name = models.CharField(max_length=80, verbose_name="Soyad")
    duty = models.CharField(max_length=120, verbose_name="Görevi")
    status = models.CharField(
        max_length=10,
        choices=StatusChoice.choices,
        default=StatusChoice.ASIL,
        verbose_name="Durum",
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="drivers",
        verbose_name="Firma",
    )
    assigned_vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name="drivers",
        verbose_name="Zimmetli Araç",
    )

    class Meta:
        verbose_name = "Şoför"
        verbose_name_plural = "Şoförler"
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.full_name} ({self.duty})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def save(self, *args, **kwargs):
        # Firma, zimmetli aracın firmasıyla tutarlı kalsın
        if self.assigned_vehicle_id:
            self.company = self.assigned_vehicle.company
        super().save(*args, **kwargs)


class VehicleTask(models.Model):
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="tasks",
        verbose_name="Bölge",
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="tasks",
        verbose_name="Firma",
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name="tasks",
        verbose_name="Araç",
    )
    driver = models.ForeignKey(
        Driver,
        on_delete=models.PROTECT,
        related_name="tasks",
        verbose_name="Şoför",
    )
    assigned_supervisor_name = models.CharField(
        max_length=120, blank=True, verbose_name="Görevlendirilen Birim Amiri"
    )
    assigned_supervisor_title = models.CharField(
        max_length=120, blank=True, verbose_name="Ünvanı"
    )
    dispatching_supervisor_name = models.CharField(
        max_length=120, blank=True, verbose_name="Aracı Sevk Eden Amir"
    )
    dispatching_supervisor_title = models.CharField(
        max_length=120, blank=True, default="Formen", verbose_name="Sevk Eden Ünvanı"
    )
    task_type = models.CharField(max_length=150, blank=True, verbose_name="Görevin Türü")
    destination = models.CharField(max_length=200, blank=True, verbose_name="Gideceği Yer")
    engine_hours_km = models.CharField(
        max_length=100, blank=True, verbose_name="Motor Saati / KM"
    )
    departure_datetime = models.DateTimeField(verbose_name="Çıkış Tarihi/Saati")
    arrival_datetime = models.DateTimeField(verbose_name="Varış Tarihi/Saati")
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_tasks",
        verbose_name="Oluşturan",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme")

    class Meta:
        verbose_name = "Görev Emri"
        verbose_name_plural = "Görev Emirleri"
        ordering = ["-departure_datetime", "-id"]

    def __str__(self):
        return f"Görev Emri #{self.display_number} - {self.vehicle.plate}"

    @property
    def display_number(self):
        if not self.pk:
            return "—"
        return Region.format_task_number(self.region, self.pk)

    def clean(self):
        if self.departure_datetime and self.arrival_datetime:
            if self.arrival_datetime <= self.departure_datetime:
                raise ValidationError(
                    {
                        "arrival_datetime": (
                            "Varış tarihi ve saati, çıkış tarihi ve saatinden sonra olmalıdır."
                        )
                    }
                )
        if self.vehicle_id and self.driver_id:
            if self.driver.assigned_vehicle_id != self.vehicle_id:
                raise ValidationError(
                    {"driver": "Seçilen şoför bu araca zimmetli değil."}
                )
        if self.vehicle_id:
            self.company = self.vehicle.company
            self.region = self.vehicle.region

    def save(self, *args, **kwargs):
        if self.vehicle_id:
            self.company = self.vehicle.company
            self.region = self.vehicle.region
        self.full_clean()
        super().save(*args, **kwargs)
