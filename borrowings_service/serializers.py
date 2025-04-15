from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from books_service.serializers import BookSerializer
from borrowings_service.models import Borrowing


DEFAULT_FIELDS = (
    "id",
    "borrow_date",
    "expected_return_date",
    "actual_return_date",
    "book",
)


class BaseUserBorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = DEFAULT_FIELDS
        read_only_fields = ("id", "borrow_date", "actual_return_date")


class BaseAdminBorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = DEFAULT_FIELDS + ("user",)


class BorrowingSerializer(BaseUserBorrowingSerializer):
    pass


class BorrowingCreateSerializer(BorrowingSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
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


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)


class BorrowingAdminSerializer(BaseAdminBorrowingSerializer):
    pass


class BorrowingAdminDetailSerializer(BorrowingAdminSerializer):
    book = BookSerializer(read_only=True)


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")
        read_only_fields = ("id", "actual_return_date")

    def validate(self, attrs):
        if self.instance.actual_return_date:
            raise serializers.ValidationError(
                "This borrowing has already been returned."
            )
        return attrs

    def save(self, **kwargs):
        borrowing = self.instance
        with transaction.atomic():
            borrowing.actual_return_date = timezone.now().date()
            borrowing.book.inventory += 1
            borrowing.book.save()
            borrowing.save()
            return borrowing
