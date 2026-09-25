from django.contrib import admin

from .models import Slot, Vehicle, ParkingTicket


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "vehicle_type",
        "level",
        "is_blocked",
    )

    list_filter = (
        "vehicle_type",
        "level",
        "is_blocked",
    )

    search_fields = (
        "code",
    )

    ordering = (
        "code",
    )


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "number",
    )

    search_fields = (
        "number",
    )

    ordering = (
        "number",
    )


@admin.register(ParkingTicket)
class ParkingTicketAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_number",
        "vehicle",
        "vehicle_type",
        "slot",
        "entry_time",
        "exit_time",
        "amount",
        "payment_method",
        "status",
    )

    list_filter = (
        "status",
        "vehicle_type",
        "payment_method",
    )

    search_fields = (
        "ticket_number",
        "vehicle__number",
    )

    ordering = (
        "-id",
    )

    readonly_fields = (
        "ticket_number",
        "entry_time",
        "exit_time",
        "stay_minutes",
        "amount",
        "paid_at",
    )