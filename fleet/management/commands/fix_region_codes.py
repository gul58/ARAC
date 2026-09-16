from django.core.management.base import BaseCommand

from fleet.models import Region


class Command(BaseCommand):
    help = "Bölge kodlarını standart tabloya göre doldurur/günceller."

    def handle(self, *args, **options):
        updated = 0
        for name, code in Region.STANDARD_REGIONS:
            region, created = Region.objects.get_or_create(
                name=name, defaults={"code": code}
            )
            if region.code != code:
                region.code = code
                region.save(update_fields=["code"])
                updated += 1
                self.stdout.write(f"{'+' if created else '~'} {name} -> {code}")
            elif created:
                self.stdout.write(f"+ {name} -> {code}")

        # Mevcut ama adı farklı yazılmış bölgeler
        for region in Region.objects.all():
            inferred = Region.code_for_name(region.name)
            if inferred and region.code != inferred:
                old = region.code
                region.code = inferred
                region.save(update_fields=["code"])
                updated += 1
                self.stdout.write(f"~ {region.name}: {old!r} -> {inferred}")

        self.stdout.write(self.style.SUCCESS(f"Tamam. Güncellenen: {updated}"))
        for r in Region.objects.order_by("name"):
            self.stdout.write(f"  {r.name}: {r.code or '—'}")
