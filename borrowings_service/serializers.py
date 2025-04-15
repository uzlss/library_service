from django.db import transaction
from rest_framework import serializers

from books_service.serializers import BookSerializer
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


class BorrowingAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingDetailSerializer(BorrowingAdminSerializer):
    book = BookSerializer(read_only=True)


class BorrowingCreateSerializer(BorrowingSerializer):
    def validate(self, attrs):
        data = super(BorrowingCreateSerializer, self).validate(attrs=attrs)
        Borrowing.validate_borrowing(
            book=attrs["book"],
            error_to_raise=serializers.ValidationError,
        )
        return data

    def create(self, validated_data):
        with transaction.atomic():
            borrowing = super().create(validated_data)
            book = validated_data["book"]
            book.inventory -= 1
            book.save()
            return borrowing
