
from django.contrib import admin
from .models import Courier, Order, CourierLocation


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "phone",
        "user",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "phone")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "phone",
        "delivery_type",
        "total_price",
        "status",
        "courier",
        "created_at",
    )

    list_filter = (
        "status",
        "delivery_type",
        "created_at",
    )

    search_fields = (
        "customer__username",
        "phone",
        "address",
    )

    list_editable = ("status", "courier")

    readonly_fields = ("created_at",)

    ordering = ("-created_at",)


@admin.register(CourierLocation)
class CourierLocationAdmin(admin.ModelAdmin):
    list_display = (
        "courier",
        "order",
        "latitude",
        "longitude",
        "updated_at",
    )

    list_filter = ("courier", "updated_at")
    readonly_fields = ("updated_at",)