from django.db import models


class Slot(models.Model):

    TWO_WHEELER = "2W"
    FOUR_WHEELER = "4W"

    VEHICLE_TYPE_CHOICES = [
        (TWO_WHEELER, "2-Wheeler"),
        (FOUR_WHEELER, "4-Wheeler"),
    ]

    code = models.CharField(
        max_length=3,
        unique=True
    )

    vehicle_type = models.CharField(
        max_length=2,
        choices=VEHICLE_TYPE_CHOICES
    )

    level = models.IntegerField(
        default=0
    )

    is_blocked = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.code


class Vehicle(models.Model):

    number = models.CharField(
        max_length=10,
        unique=True
    )

    def __str__(self):
        return self.number


class ParkingTicket(models.Model):

    PARKED = "PARKED"
    PAID = "PAID"

    STATUS_CHOICES = [
        (PARKED, "Parked"),
        (PAID, "Paid"),
    ]

    CASH = "CASH"
    UPI = "UPI"

    PAYMENT_CHOICES = [
        (CASH, "Cash"),
        (UPI, "UPI"),
    ]

    ticket_number = models.CharField(
        max_length=20,
        unique=True
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT
    )

    vehicle_type = models.CharField(
        max_length=2,
        choices=Slot.VEHICLE_TYPE_CHOICES
    )

    slot = models.ForeignKey(
        Slot,
        on_delete=models.PROTECT
    )

    entry_time = models.DateTimeField()

    exit_time = models.DateTimeField(
        null=True,
        blank=True
    )

    stay_minutes = models.IntegerField(
        null=True,
        blank=True
    )

    amount = models.IntegerField(
        default=0
    )

    payment_method = models.CharField(
        max_length=4,
        choices=PAYMENT_CHOICES,
        null=True,
        blank=True
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=6,
        choices=STATUS_CHOICES,
        default=PARKED
    )

    def __str__(self):
        return self.ticket_number