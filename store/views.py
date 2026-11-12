
import json
import math
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone

from .models import Courier, Order, CourierLocation


# =====================================================
# 1. ДӘРІХАНАНЫҢ БАСТЫ БЕТІ
# =====================================================

def pharmacy_home(request):
    return render(
        request,
        "pharmacy_information_system.html"
    )


# =====================================================
# 2. КУРЬЕРДІҢ ЖҮЙЕГЕ КІРУІ
# =====================================================

def courier_login(request):

    if request.user.is_authenticated:
        if Courier.objects.filter(
            user=request.user,
            is_active=True
        ).exists():
            return redirect("courier_dashboard")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and Courier.objects.filter(
            user=user,
            is_active=True
        ).exists():
            login(request, user)
            return redirect("courier_dashboard")

        return render(
            request,
            "courier_login.html",
            {
                "error": (
                    "Логин немесе құпиясөз қате, "
                    "не курьер аккаунты белсенді емес."
                )
            }
        )

    return render(
        request,
        "courier_login.html"
    )


# =====================================================
# 3. КУРЬЕРДІҢ ЖЕКЕ КАБИНЕТІ
# =====================================================

@login_required(login_url="/courier/login/")
def courier_dashboard(request):

    courier = Courier.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    if courier is None:
        return HttpResponseForbidden(
            "Сізде курьер кабинетіне кіру құқығы жоқ."
        )

    orders = Order.objects.filter(
        courier=courier,
        delivery_type="courier"
    ).exclude(
        status__in=["delivered", "cancelled"]
    ).select_related(
        "customer"
    ).order_by("-created_at")

    context = {
        "courier": courier,
        "orders": orders,
        "orders_count": orders.count(),
    }

    return render(
        request,
        "courier_dashboard.html",
        context
    )


# =====================================================
# 4. КУРЬЕРДІҢ ЖҮЙЕДЕН ШЫҒУЫ
# =====================================================

@require_POST
def courier_logout(request):

    logout(request)

    return redirect("courier_login")


# =====================================================
# 5. КУРЬЕРДІҢ GPS КООРДИНАТТАРЫН САҚТАУ
# =====================================================

@login_required(login_url="/courier/login/")
@require_POST
def update_courier_location(request, order_id):

    courier = Courier.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    if courier is None:
        return JsonResponse(
            {
                "success": False,
                "error": "Курьерге рұқсат жоқ."
            },
            status=403
        )

    order = get_object_or_404(
        Order,
        id=order_id,
        courier=courier,
        delivery_type="courier"
    )

    if order.status not in ["accepted", "on_way"]:
        return JsonResponse(
            {
                "success": False,
                "error": "Бұл тапсырыс үшін GPS қолжетімсіз."
            },
            status=400
        )

    try:
        data = json.loads(request.body)

        latitude = float(data["latitude"])
        longitude = float(data["longitude"])

        if not (
            math.isfinite(latitude)
            and math.isfinite(longitude)
            and -90 <= latitude <= 90
            and -180 <= longitude <= 180
        ):
            raise ValueError("Invalid GPS coordinates")

    except (
        ValueError,
        TypeError,
        KeyError,
        json.JSONDecodeError
    ):
        return JsonResponse(
            {
                "success": False,
                "error": "GPS координаттары дұрыс емес."
            },
            status=400
        )

    location = CourierLocation.objects.create(
        courier=courier,
        order=order,
        latitude=latitude,
        longitude=longitude
    )

    return JsonResponse({
        "success": True,
        "message": "GPS координаттары сақталды.",
        "order_id": order.id,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "updated_at": location.updated_at.isoformat()
    })


# =====================================================
# 6. АДМИНГЕ КУРЬЕРЛЕРДІҢ GPS ДЕРЕКТЕРІН БЕРУ
# =====================================================

@staff_member_required
@require_GET
def admin_courier_locations(request):

    active_orders = Order.objects.filter(
        delivery_type="courier",
        status__in=["accepted", "on_way"],
        courier__isnull=False,
        courier__is_active=True
    ).select_related(
        "courier"
    ).order_by("-created_at")

    results = []

    for order in active_orders:

        location = CourierLocation.objects.filter(
            order=order,
            courier=order.courier
        ).order_by(
            "-updated_at",
            "-id"
        ).first()

        if location is None:
            continue

        age_seconds = (
            timezone.now() - location.updated_at
        ).total_seconds()

        is_fresh = 0 <= age_seconds <= 30

        results.append({
            "order_id": order.id,
            "courier_id": order.courier.id,
            "courier": order.courier.name,
            "courier_phone": order.courier.phone,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "updated_at": location.updated_at.isoformat(),
            "is_fresh": is_fresh,
            "status": order.status,
            "status_display": order.get_status_display()
        })

    return JsonResponse({
        "success": True,
        "count": len(results),
        "couriers": results
    })


# =====================================================
# 7. АДМИННІҢ GPS БАҚЫЛАУ БЕТІ
# =====================================================

@staff_member_required
@require_GET
def admin_tracking_page(request):

    return render(
        request,
        "admin_tracking.html"
    )
