from rest_framework import serializers

from ..models import Book, SupplierCountry

# Shown when supplier_country is not one of the enum values.
_SUPPLIER_COUNTRY_VALID = ", ".join(SupplierCountry.values)


class SupplierCountryField(serializers.ChoiceField):
    # Accepts any case; stored value is always uppercase in the DB
    def to_internal_value(self, data):
        if isinstance(data, str):
            data = data.strip().upper()
        return super().to_internal_value(data)


class BookSerializer(serializers.ModelSerializer):
    isbn = serializers.CharField(read_only=True)
    supplier_country = SupplierCountryField(
        choices=SupplierCountry.choices,
        error_messages={
            "invalid_choice": '"{input}" is not a valid choice. Valid options: '
            + _SUPPLIER_COUNTRY_VALID
            + ".",
        },
    )

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "isbn",
            "cost_usd",
            "selling_price_local",
            "stock_quantity",
            "category",
            "supplier_country",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "isbn",
            "selling_price_local",
            "created_at",
            "updated_at",
        )
