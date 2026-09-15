from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from fleet.models import (
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


class Command(BaseCommand):
    help = "Örnek İhale/Formen kullanıcıları ve master verileri oluşturur."

    def handle(self, *args, **options):
        ihale, created = User.objects.get_or_create(
            username="cagla",
            defaults={
                "role": UserRole.IHALE,
                "first_name": "Çağla",
                "is_staff": True,
            },
        )
        if created or not ihale.has_usable_password():
            ihale.set_password("cagla123")
            ihale.role = UserRole.IHALE
            ihale.save()
        self.stdout.write(self.style.SUCCESS("İhale kullanıcısı: cagla / cagla123"))

        regions = {}
        for name in ("Derince", "Başiskele", "Kartepe"):
            regions[name], _ = Region.objects.get_or_create(name=name)

        company, _ = Company.objects.get_or_create(name="KÜRE")

        def ensure_formen(username, first, last, region_name, password="formen123"):
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "role": UserRole.FORMEN,
                    "first_name": first,
                    "last_name": last,
                },
            )
            if created or not user.has_usable_password():
                user.set_password(password)
                user.role = UserRole.FORMEN
                user.first_name = first
                user.last_name = last
                user.save()
            foreman, _ = Foreman.objects.get_or_create(
                user=user,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "region": regions[region_name],
                    "status": StatusChoice.ASIL,
                },
            )
            foreman.first_name = first
            foreman.last_name = last
            foreman.region = regions[region_name]
            foreman.status = StatusChoice.ASIL
            foreman.save()
            return foreman

        f_yanik = ensure_formen("m.yanik", "Mustafa", "Yanık", "Derince")
        f_muhammet = ensure_formen("muhammet", "Muhammet", "Yılmaz", "Derince")

        vehicle, _ = Vehicle.objects.get_or_create(
            plate="41 ABC 123",
            defaults={
                "vehicle_type": "çekici",
                "status": StatusChoice.ASIL,
                "company": company,
                "region": regions["Derince"],
                "primary_foreman": f_yanik,
                "backup_foreman": None,
            },
        )
        vehicle.company = company
        vehicle.region = regions["Derince"]
        vehicle.primary_foreman = f_yanik
        vehicle.vehicle_type = "çekici"
        vehicle.status = StatusChoice.ASIL
        vehicle.save()

        asil_driver, _ = Driver.objects.get_or_create(
            first_name="ALİ",
            last_name="CAN",
            assigned_vehicle=vehicle,
            status=StatusChoice.ASIL,
            defaults={
                "duty": "ÇEKİCİ OPERATÖRÜ",
                "company": company,
            },
        )
        asil_driver.duty = "ÇEKİCİ OPERATÖRÜ"
        asil_driver.company = company
        asil_driver.save()

        for first, last in (("Mehmet", "Kaya"), ("Hasan", "Çelik")):
            Driver.objects.get_or_create(
                first_name=first,
                last_name=last,
                assigned_vehicle=vehicle,
                status=StatusChoice.YEDEK,
                defaults={
                    "duty": "ÇEKİCİ OPERATÖRÜ",
                    "company": company,
                },
            )

        if not VehicleTask.objects.exists():
            now = timezone.localtime()
            departure = now.replace(hour=8, minute=30, second=0, microsecond=0)
            arrival = departure + timedelta(hours=8, minutes=15)
            VehicleTask.objects.create(
                region=regions["Derince"],
                company=company,
                vehicle=vehicle,
                driver=asil_driver,
                assigned_supervisor_name="",
                assigned_supervisor_title="",
                dispatching_supervisor_name=f_muhammet.full_name,
                dispatching_supervisor_title="Formen",
                task_type="Yol bakım",
                destination="Derince şantiye",
                engine_hours_km="1250",
                departure_datetime=departure,
                arrival_datetime=arrival,
                created_by=f_muhammet.user,
            )

        self.stdout.write(self.style.SUCCESS("Formen: muhammet / formen123 (Derince)"))
        self.stdout.write(self.style.SUCCESS("Formen: m.yanik / formen123 (Derince)"))
        self.stdout.write(self.style.SUCCESS("Örnek veriler hazır."))
