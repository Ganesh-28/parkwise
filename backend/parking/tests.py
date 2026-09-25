from django.test import SimpleTestCase

from .models import Slot
from .services import (
    calculate_fee,
    normalize_vehicle_number,
    normalize_vehicle_type
)


class ParkingServiceTests(SimpleTestCase):

    def test_vehicle_number_normalization(self):

        result = normalize_vehicle_number(
            "ka 01 ab 1234"
        )

        self.assertEqual(
            result,
            "KA01AB1234"
        )

    def test_invalid_vehicle_number(self):

        result = normalize_vehicle_number(
            "ABC"
        )

        self.assertIsNone(result)

    def test_vehicle_type(self):

        self.assertEqual(
            normalize_vehicle_type("2W"),
            Slot.TWO_WHEELER
        )

        self.assertEqual(
            normalize_vehicle_type("4W"),
            Slot.FOUR_WHEELER
        )

    def test_fee_60_minutes(self):

        self.assertEqual(
            calculate_fee(
                60,
                Slot.TWO_WHEELER
            ),
            0
        )

        self.assertEqual(
            calculate_fee(
                60,
                Slot.FOUR_WHEELER
            ),
            0
        )

    def test_fee_61_minutes(self):

        self.assertEqual(
            calculate_fee(
                61,
                Slot.TWO_WHEELER
            ),
            10
        )

        self.assertEqual(
            calculate_fee(
                61,
                Slot.FOUR_WHEELER
            ),
            50
        )

    def test_fee_180_minutes(self):

        self.assertEqual(
            calculate_fee(
                180,
                Slot.TWO_WHEELER
            ),
            10
        )

        self.assertEqual(
            calculate_fee(
                180,
                Slot.FOUR_WHEELER
            ),
            50
        )

    def test_fee_181_minutes(self):

        self.assertEqual(
            calculate_fee(
                181,
                Slot.TWO_WHEELER
            ),
            20
        )

        self.assertEqual(
            calculate_fee(
                181,
                Slot.FOUR_WHEELER
            ),
            80
        )

    def test_fee_320_minutes(self):

        self.assertEqual(
            calculate_fee(
                320,
                Slot.TWO_WHEELER
            ),
            40
        )

        self.assertEqual(
            calculate_fee(
                320,
                Slot.FOUR_WHEELER
            ),
            140
        )

    def test_fee_1560_minutes(self):

        self.assertEqual(
            calculate_fee(
                1560,
                Slot.TWO_WHEELER
            ),
            200
        )

        self.assertEqual(
            calculate_fee(
                1560,
                Slot.FOUR_WHEELER
            ),
            600
        )