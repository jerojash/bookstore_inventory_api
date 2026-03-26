from django.db import models


class ExchangeRate(models.Model):
    currency_code = models.CharField(max_length=3, unique=True)
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["currency_code"]

    def __str__(self) -> str:
        return f"{self.currency_code}={self.rate}"

