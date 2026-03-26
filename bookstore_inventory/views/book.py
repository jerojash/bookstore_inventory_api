from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Book
from ..serializers import BookSerializer


# Services for the Book model.
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    _profit_multiplier = Decimal("1.40")
    _profit_margin = Decimal("0.40")
    _two_places = Decimal("0.01")


    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        category = request.query_params.get("category")
        if not category:
            return Response([])

        books = self.get_queryset().filter(category=category)

        serializer = self.get_serializer(books, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)



    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request):
        threshold_raw = request.query_params.get("threshold", "10")
        
        try:
            threshold = int(threshold_raw)


        except ValueError:
            return Response(
                {"error": "threshold must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        books = self.get_queryset().filter(stock_quantity__lte=threshold)
        serializer = self.get_serializer(books, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @csrf_exempt
    @transaction.atomic
    @action(detail=True, methods=["post"], url_path="calculate-price")
    def calculate_price(self, request, pk=None):
        book = self.get_object()

        currency_code = request.data.get("currency")

        if not currency_code:
            return Response(
                {"error": "currency is required in the request body"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mock exchange rate for now
        exchange_rate = Decimal("400")

        local_cost = (book.cost_usd * exchange_rate).quantize(
            self._two_places, rounding=ROUND_HALF_UP
        )

        selling_price = (local_cost * self._profit_multiplier).quantize(
            self._two_places, rounding=ROUND_HALF_UP
        )

        book.selling_price_local = selling_price

        book.save(update_fields=["selling_price_local", "updated_at"])

        return Response(
            {
                "book_id": book.id,
                "cost_usd": str(book.cost_usd),
                "local_currency": currency_code,
                "exchange_rate": str(exchange_rate),
                "local_cost": str(local_cost),
                "profit_margin": str(self._profit_margin),
                "selling_price_local": str(selling_price),
            },
            status=status.HTTP_200_OK,
        )


    def update(self, request, *args, **kwargs):
        # Treat PUT like PATCH to allow partial updates.
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

