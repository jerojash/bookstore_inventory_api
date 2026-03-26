from rest_framework import serializers

from ..models import Book, SupplierCountry


class BookSerializer(serializers.ModelSerializer):
    isbn = serializers.CharField(read_only=True)
    supplier_country = serializers.ChoiceField(choices=SupplierCountry.choices)

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

from rest_framework import serializers

from ..models import Book, SupplierCountry


class BookSerializer(serializers.ModelSerializer):
    isbn = serializers.CharField(read_only=True)
    supplier_country = serializers.ChoiceField(choices=SupplierCountry.choices)

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

