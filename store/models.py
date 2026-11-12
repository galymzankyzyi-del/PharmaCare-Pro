
from django.db import models
from django.conf import settings


class Courier(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courier_profile"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "Жаңа тапсырыс"),
        ("accepted", "Қабылданды"),
        ("on_way", "Жолға шықты"),
        ("delivered", "Жеткізілді"),
        ("cancelled", "Бас тартылды"),
    ]

    DELIVERY_CHOICES = [
        ("courier", "Курьер арқылы"),
        ("pickup", "Өзі алып кету"),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pharmacy_orders"
    )
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    delivery_type = models.CharField(
        max_length=20,
        choices=DELIVERY_CHOICES,
        default="pickup"
    )
    payment_method = models.CharField(max_length=30)
    payment_receipt = models.ImageField(
        upload_to="receipts/",
        blank=True,
        null=True
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new"
    )
    courier = models.ForeignKey(
        Courier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Тапсырыс #{self.id}"


class CourierLocation(models.Model):
    courier = models.ForeignKey(
        Courier,
        on_delete=models.CASCADE,
        related_name="locations"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="locations"
    )
    latitude = models.FloatField()
    longitude = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.courier.name}: {self.latitude}, {self.longitude}"
