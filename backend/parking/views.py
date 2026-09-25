import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import (
    create_entry,
    process_exit,
    get_dashboard_data
)

from .services import create_entry, process_exit


@csrf_exempt
def entry(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "code": "METHOD_NOT_ALLOWED",
                "message": "Only POST requests are allowed."
            },
            status=405
        )

    try:
        data = json.loads(request.body)

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "success": False,
                "code": "INVALID_JSON",
                "message": "Invalid JSON request."
            },
            status=400
        )

    vehicle_number = data.get("vehicle_number")
    vehicle_type = data.get("vehicle_type")

    result = create_entry(
        vehicle_number,
        vehicle_type
    )

    if not result["success"]:

        status_code = 400

        if result["code"] == "LOT_FULL":
            status_code = 409

        elif result["code"] == "ALREADY_PARKED":
            status_code = 409

        return JsonResponse(
            result,
            status=status_code
        )

    ticket = result["ticket"]

    return JsonResponse(
        {
            "success": True,
            "ticket_number": ticket.ticket_number,
            "vehicle_number": ticket.vehicle.number,
            "vehicle_type": ticket.vehicle_type,
            "slot": ticket.slot.code,
            "entry_time": ticket.entry_time.isoformat(),
            "message": "Vehicle entry created successfully."
        },
        status=201
    )
    
   
@csrf_exempt
def exit_parking(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "code": "METHOD_NOT_ALLOWED",
                "message": "Only POST requests are allowed."
            },
            status=405
        )

    try:
        data = json.loads(request.body)

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "success": False,
                "code": "INVALID_JSON",
                "message": "Invalid JSON request."
            },
            status=400
        )

    ticket_number = data.get("ticket_number")
    payment_method = data.get("payment_method")

    result = process_exit(
        ticket_number,
        payment_method
    )

    if not result["success"]:

        status_code = 400

        if result["code"] in [
            "NOT_PARKED",
            "ALREADY_PAID"
        ]:
            status_code = 409

        return JsonResponse(
            result,
            status=status_code
        )

    ticket = result["ticket"]

    return JsonResponse(
        {
            "success": True,
            "ticket_number": ticket.ticket_number,
            "vehicle_number": ticket.vehicle.number,
            "vehicle_type": ticket.vehicle_type,
            "slot": ticket.slot.code,
            "entry_time": ticket.entry_time.isoformat(),
            "exit_time": ticket.exit_time.isoformat(),
            "stay_minutes": ticket.stay_minutes,
            "amount": ticket.amount,
            "payment_method": ticket.payment_method,
            "paid_at": ticket.paid_at.isoformat(),
            "message": "Payment completed successfully."
        },
        status=200
    )
def dashboard(request):

    if request.method != "GET":
        return JsonResponse(
            {
                "success": False,
                "code": "METHOD_NOT_ALLOWED",
                "message": "Only GET requests are allowed."
            },
            status=405
        )

    data = get_dashboard_data()

    return JsonResponse({
        "success": True,
        **data
    })
    
from django.shortcuts import render


def entry_page(request):
    return render(request, "entry.html")


def exit_page(request):
    return render(request, "exit.html")


def dashboard_page(request):
    return render(request, "dashboard.html") 