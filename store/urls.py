
from django.urls import path
from . import views

urlpatterns = [

    # Дәріхананың басты беті
    path(
        "",
        views.pharmacy_home,
        name="pharmacy_home"
    ),

    # Курьердің кіру беті
    path(
        "courier/login/",
        views.courier_login,
        name="courier_login"
    ),

    # Курьердің жеке кабинеті
    path(
        "courier/",
        views.courier_dashboard,
        name="courier_dashboard"
    ),

    # Курьердің жүйеден шығуы
    path(
        "courier/logout/",
        views.courier_logout,
        name="courier_logout"
    ),

    # GPS координаттарын серверге жіберу
    path(
        "api/orders/<int:order_id>/location/",
        views.update_courier_location,
        name="update_courier_location"
    ),

    # Админге GPS деректерін беру
    path(
        "api/admin/couriers/locations/",
        views.admin_courier_locations,
        name="admin_courier_locations"
    ),

    # Админнің GPS бақылау картасы
    path(
        "admin-tracking/",
        views.admin_tracking_page,
        name="admin_tracking_page"
    ),

]
