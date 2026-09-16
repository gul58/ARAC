from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from fleet.models import (
    Company,
    Driver,
    Foreman,
    Region,
    StatusChoice,
    UserRole,
    Vehicle,
    VehicleTask,
)


User = get_user_model()


class AuthorizationAndTaskTests(TestCase):
    def setUp(self):
        self.region_a = Region.objects.create(name="Derince", code="DRN")
        self.region_b = Region.objects.create(name="Kartepe", code="KRT")
        self.company = Company.objects.create(name="KÜRE")

        self.ihale = User.objects.create_user(
            username="ihale1", password="pass12345", role=UserRole.IHALE
        )
        self.formen_a_user = User.objects.create_user(
            username="formen_a", password="pass12345", role=UserRole.FORMEN
        )
        self.formen_b_user = User.objects.create_user(
            username="formen_b", password="pass12345", role=UserRole.FORMEN
        )
        self.formen_a = Foreman.objects.create(
            user=self.formen_a_user,
            first_name="A",
            last_name="Formen",
            region=self.region_a,
            status=StatusChoice.ASIL,
        )
        self.formen_b = Foreman.objects.create(
            user=self.formen_b_user,
            first_name="B",
            last_name="Formen",
            region=self.region_b,
            status=StatusChoice.ASIL,
        )
        self.vehicle_a = Vehicle.objects.create(
            plate="41 AAA 01",
            vehicle_type="çekici",
            status=StatusChoice.ASIL,
            company=self.company,
            region=self.region_a,
            primary_foreman=self.formen_a,
        )
        self.vehicle_b = Vehicle.objects.create(
            plate="41 BBB 02",
            vehicle_type="kamyon",
            status=StatusChoice.ASIL,
            company=self.company,
            region=self.region_b,
            primary_foreman=self.formen_b,
        )
        self.driver_a = Driver.objects.create(
            first_name="Ali",
            last_name="Can",
            duty="Operatör",
            status=StatusChoice.ASIL,
            company=self.company,
            assigned_vehicle=self.vehicle_a,
        )
        self.driver_b = Driver.objects.create(
            first_name="Veli",
            last_name="Demir",
            duty="Şoför",
            status=StatusChoice.ASIL,
            company=self.company,
            assigned_vehicle=self.vehicle_b,
        )
        now = timezone.now()
        self.task_b = VehicleTask.objects.create(
            region=self.region_b,
            company=self.company,
            vehicle=self.vehicle_b,
            driver=self.driver_b,
            departure_datetime=now,
            arrival_datetime=now + timedelta(hours=2),
            created_by=self.formen_b_user,
        )

    def test_formen_cannot_access_other_region_task(self):
        client = Client()
        client.login(username="formen_a", password="pass12345")
        url = reverse("formen_task_edit", args=[self.task_b.pk])
        response = client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_formen_cannot_access_ihale_pages(self):
        client = Client()
        client.login(username="formen_a", password="pass12345")
        response = client.get(reverse("ihale_regions"))
        self.assertEqual(response.status_code, 403)

    def test_ihale_cannot_access_formen_task_create(self):
        client = Client()
        client.login(username="ihale1", password="pass12345")
        response = client.get(reverse("formen_task_create"))
        self.assertEqual(response.status_code, 403)

    def test_arrival_must_be_after_departure(self):
        client = Client()
        client.login(username="formen_a", password="pass12345")
        response = client.post(
            reverse("formen_task_create"),
            {
                "assigned_supervisor_name": "",
                "assigned_supervisor_title": "",
                "dispatching_supervisor_name": "A Formen",
                "dispatching_supervisor_title": "Formen",
                "task_type": "Bakım",
                "destination": "Şantiye",
                "vehicle": self.vehicle_a.pk,
                "driver": self.driver_a.pk,
                "engine_hours_km": "100",
                "departure_local": "10.09.2026 16:00",
                "arrival_local": "10.09.2026 14:00",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sonra olmalıdır")
        self.assertEqual(VehicleTask.objects.filter(region=self.region_a).count(), 0)

    def test_valid_task_create(self):
        client = Client()
        client.login(username="formen_a", password="pass12345")
        response = client.post(
            reverse("formen_task_create"),
            {
                "assigned_supervisor_name": "",
                "assigned_supervisor_title": "",
                "dispatching_supervisor_name": "A Formen",
                "dispatching_supervisor_title": "Formen",
                "task_type": "Bakım",
                "destination": "Şantiye",
                "vehicle": self.vehicle_a.pk,
                "driver": self.driver_a.pk,
                "engine_hours_km": "100",
                "departure_local": "10.09.2026 08:30",
                "arrival_local": "10.09.2026 16:45",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(VehicleTask.objects.filter(region=self.region_a).count(), 1)
