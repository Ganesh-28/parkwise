from django.core.management.base import BaseCommand

from parking.models import Slot


class Command(BaseCommand):

    help = "Create Parkwise parking slots"

    def handle(self, *args, **kwargs):

        # Create B01 - B12
        for i in range(1, 13):

            code = f"B{i:02d}"

            Slot.objects.get_or_create(
                code=code,
                defaults={
                    "vehicle_type": Slot.TWO_WHEELER,
                    "level": 0,
                    "is_blocked": False,
                }
            )

        # Create C01 - C08
        for i in range(1, 9):

            code = f"C{i:02d}"

            Slot.objects.get_or_create(
                code=code,
                defaults={
                    "vehicle_type": Slot.FOUR_WHEELER,
                    "level": 1,
                    "is_blocked": code == "C08",
                }
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Parkwise parking slots created successfully."
            )
        )
        