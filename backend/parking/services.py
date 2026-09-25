import math

from django.db import models, transaction
from django.utils import timezone

from .models import Slot, Vehicle, ParkingTicket


def normalize_vehicle_number(vehicle_number):
    if not vehicle_number:
        return None

    vehicle_number = "".join(str(vehicle_number).split())
    vehicle_number = vehicle_number.upper()

    if not vehicle_number.isalnum():
        return None

    if not 6 <= len(vehicle_number) <= 10:
        return None

    return vehicle_number


def normalize_vehicle_type(vehicle_type):
    if not vehicle_type:
        return None

    vehicle_type = str(vehicle_type).strip().upper()

    if vehicle_type in ["2W", "2-WHEELER", "2 WHEELER"]:
        return Slot.TWO_WHEELER

    if vehicle_type in ["4W", "4-WHEELER", "4 WHEELER"]:
        return Slot.FOUR_WHEELER

    return None


def calculate_fee(stay_minutes, vehicle_type):
    if stay_minutes <= 60:
        return 0

    if stay_minutes <= 180:
        if vehicle_type == Slot.TWO_WHEELER:
            return 10

        if vehicle_type == Slot.FOUR_WHEELER:
            return 50

    if vehicle_type == Slot.TWO_WHEELER:
        base_fee = 10
        hourly_rate = 10
        daily_maximum = 100
    else:
        base_fee = 50
        hourly_rate = 30
        daily_maximum = 300

    extra_minutes = stay_minutes - 180
    extra_hours = math.ceil(extra_minutes / 60)

    fee = base_fee + (extra_hours * hourly_rate)

    days = math.ceil(stay_minutes / 1440)
    maximum_fee = daily_maximum * days

    return min(fee, maximum_fee)


def calculate_stay_minutes(entry_time, exit_time):
    duration = exit_time - entry_time
    seconds = duration.total_seconds()

    minutes = math.ceil(seconds / 60)

    return max(0, minutes)


def get_free_slot(vehicle_type):
    if vehicle_type == Slot.TWO_WHEELER:

        slots = (
            Slot.objects
            .select_for_update()
            .filter(
                vehicle_type=Slot.TWO_WHEELER,
                is_blocked=False
            )
            .order_by("code")
        )

        for slot in slots:

            occupied = ParkingTicket.objects.filter(
                slot=slot,
                status=ParkingTicket.PARKED
            ).exists()

            if not occupied:
                return slot

        slots = (
            Slot.objects
            .select_for_update()
            .filter(
                vehicle_type=Slot.FOUR_WHEELER,
                is_blocked=False
            )
            .order_by("code")
        )

        for slot in slots:

            occupied = ParkingTicket.objects.filter(
                slot=slot,
                status=ParkingTicket.PARKED
            ).exists()

            if not occupied:
                return slot

    elif vehicle_type == Slot.FOUR_WHEELER:

        slots = (
            Slot.objects
            .select_for_update()
            .filter(
                vehicle_type=Slot.FOUR_WHEELER,
                is_blocked=False
            )
            .order_by("code")
        )

        for slot in slots:

            occupied = ParkingTicket.objects.filter(
                slot=slot,
                status=ParkingTicket.PARKED
            ).exists()

            if not occupied:
                return slot

    return None


def generate_ticket_number():
    last_ticket = (
        ParkingTicket.objects
        .select_for_update()
        .order_by("-id")
        .first()
    )

    if not last_ticket:
        number = 1

    else:
        try:
            last_number = int(
                last_ticket.ticket_number.replace("PK-", "")
            )

            number = last_number + 1

        except ValueError:
            number = ParkingTicket.objects.count() + 1

    return f"PK-{number:04d}"


@transaction.atomic
def create_entry(vehicle_number, vehicle_type):

    vehicle_number = normalize_vehicle_number(vehicle_number)

    if not vehicle_number:
        return {
            "success": False,
            "code": "INVALID_VEHICLE",
            "message": "Invalid vehicle number."
        }

    vehicle_type = normalize_vehicle_type(vehicle_type)

    if not vehicle_type:
        return {
            "success": False,
            "code": "INVALID_VEHICLE",
            "message": "Invalid vehicle type."
        }

    vehicle = (
        Vehicle.objects
        .select_for_update()
        .filter(number=vehicle_number)
        .first()
    )

    if not vehicle:
        vehicle = Vehicle.objects.create(
            number=vehicle_number
        )

    already_parked = ParkingTicket.objects.filter(
        vehicle=vehicle,
        status=ParkingTicket.PARKED
    ).exists()

    if already_parked:
        return {
            "success": False,
            "code": "ALREADY_PARKED",
            "message": "Vehicle is already parked."
        }

    slot = get_free_slot(vehicle_type)

    if not slot:
        return {
            "success": False,
            "code": "LOT_FULL",
            "message": "No parking slot available."
        }

    ticket_number = generate_ticket_number()
    entry_time = timezone.now()

    ticket = ParkingTicket.objects.create(
        ticket_number=ticket_number,
        vehicle=vehicle,
        vehicle_type=vehicle_type,
        slot=slot,
        entry_time=entry_time,
        status=ParkingTicket.PARKED
    )

    return {
        "success": True,
        "ticket": ticket
    }


@transaction.atomic
def process_exit(ticket_number, payment_method):

    if not ticket_number:
        return {
            "success": False,
            "code": "INVALID_TICKET",
            "message": "Ticket number is required."
        }

    ticket_number = str(ticket_number).strip().upper()

    if not payment_method:
        return {
            "success": False,
            "code": "INVALID_PAYMENT_METHOD",
            "message": "Payment method is required."
        }

    payment_method = str(payment_method).strip().upper()

    if payment_method not in [
        ParkingTicket.CASH,
        ParkingTicket.UPI
    ]:
        return {
            "success": False,
            "code": "INVALID_PAYMENT_METHOD",
            "message": "Payment method must be CASH or UPI."
        }

    ticket = (
        ParkingTicket.objects
        .select_for_update()
        .select_related("vehicle", "slot")
        .filter(ticket_number=ticket_number)
        .first()
    )

    if not ticket:
        return {
            "success": False,
            "code": "NOT_PARKED",
            "message": "Ticket not found."
        }

    if ticket.status == ParkingTicket.PAID:
        return {
            "success": False,
            "code": "ALREADY_PAID",
            "message": "This ticket has already been paid."
        }

    exit_time = timezone.now()

    stay_minutes = calculate_stay_minutes(
        ticket.entry_time,
        exit_time
    )

    amount = calculate_fee(
        stay_minutes,
        ticket.vehicle_type
    )

    ticket.exit_time = exit_time
    ticket.stay_minutes = stay_minutes
    ticket.amount = amount
    ticket.payment_method = payment_method
    ticket.paid_at = exit_time
    ticket.status = ParkingTicket.PAID

    ticket.save(
        update_fields=[
            "exit_time",
            "stay_minutes",
            "amount",
            "payment_method",
            "paid_at",
            "status"
        ]
    )

    return {
        "success": True,
        "ticket": ticket
    }


def get_dashboard_data():

    total_slots = Slot.objects.count()

    blocked_slots = Slot.objects.filter(
        is_blocked=True
    ).count()

    occupied_slot_ids = set(
        ParkingTicket.objects
        .filter(status=ParkingTicket.PARKED)
        .values_list("slot_id", flat=True)
    )

    occupied_slots = len(occupied_slot_ids)

    available_slots = (
        total_slots
        - blocked_slots
        - occupied_slots
    )

    two_wheeler_occupied = ParkingTicket.objects.filter(
        status=ParkingTicket.PARKED,
        vehicle_type=Slot.TWO_WHEELER
    ).count()

    four_wheeler_occupied = ParkingTicket.objects.filter(
        status=ParkingTicket.PARKED,
        vehicle_type=Slot.FOUR_WHEELER
    ).count()

    total_revenue = (
        ParkingTicket.objects
        .filter(status=ParkingTicket.PAID)
        .aggregate(
            total=models.Sum("amount")
        )["total"]
        or 0
    )

    all_slots = (
        Slot.objects
        .all()
        .order_by("code")
    )

    slot_data = []

    for slot in all_slots:

        if slot.is_blocked:
            status = "BLOCKED"

        elif slot.id in occupied_slot_ids:
            status = "OCCUPIED"

        else:
            status = "AVAILABLE"

        slot_data.append({
            "code": slot.code,
            "vehicle_type": slot.vehicle_type,
            "level": slot.level,
            "is_blocked": slot.is_blocked,
            "status": status
        })

    pending_tickets = (
        ParkingTicket.objects
        .select_related("vehicle", "slot")
        .filter(status=ParkingTicket.PARKED)
        .order_by("-id")
    )

    pending_data = []

    for ticket in pending_tickets:

        pending_data.append({
            "ticket_number": ticket.ticket_number,
            "vehicle_number": ticket.vehicle.number,
            "vehicle_type": ticket.vehicle_type,
            "slot": ticket.slot.code,
            "entry_time": ticket.entry_time.isoformat()
        })

    recent_tickets = (
        ParkingTicket.objects
        .select_related("vehicle", "slot")
        .order_by("-id")[:10]
    )

    recent_data = []

    for ticket in recent_tickets:

        recent_data.append({
            "ticket_number": ticket.ticket_number,
            "vehicle_number": ticket.vehicle.number,
            "vehicle_type": ticket.vehicle_type,
            "slot": ticket.slot.code,
            "status": ticket.status,
            "entry_time": ticket.entry_time.isoformat(),
            "exit_time": (
                ticket.exit_time.isoformat()
                if ticket.exit_time
                else None
            ),
            "amount": ticket.amount,
            "payment_method": ticket.payment_method
        })

    return {
        "total_slots": total_slots,
        "blocked_slots": blocked_slots,
        "occupied_slots": occupied_slots,
        "available_slots": available_slots,
        "two_wheeler_occupied": two_wheeler_occupied,
        "four_wheeler_occupied": four_wheeler_occupied,
        "total_revenue": total_revenue,
        "slots": slot_data,
        "pending_tickets": pending_data,
        "recent_tickets": recent_data
    }