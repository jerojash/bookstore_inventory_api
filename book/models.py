import secrets

from django.core.validators import RegexValidator
from django.db import models

_isbn_digits_validator = RegexValidator(
    regex=r"^\d{10,13}$",
    message="ISBN must be 10-13 digits only.",
)


class SupplierCountry(models.TextChoices):
    US = "US", "US"
    ES = "ES", "ES"
    VE = "VE", "VE"
    CO = "CO", "CO"
    MX = "MX", "MX"
    AR = "AR", "AR"


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(
        max_length=13,
        unique=True,
        validators=[_isbn_digits_validator],
        editable=False,
        blank=True,
    )
    cost_usd = models.DecimalField(max_digits=12, decimal_places=2)
    selling_price_local = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=255)
    supplier_country = models.CharField(
        max_length=2,
        choices=SupplierCountry.choices,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        if not self.isbn:
            self.isbn = self._generate_isbn()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_isbn() -> str:
        while True:
            candidate = "".join(secrets.choice("0123456789") for _ in range(13))
            if not Book.objects.filter(isbn=candidate).exists():
                return candidate

    def __str__(self) -> str:
        return f"{self.title} ({self.isbn})"
