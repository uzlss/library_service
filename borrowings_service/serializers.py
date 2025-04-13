from rest_framework import serializers

import books_service.serializers
from borrowings_service.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )


class BorrowingDetailSerializer(BorrowingSerializer):
    book = books_service.serializers.BookSerializer(read_only=True)
