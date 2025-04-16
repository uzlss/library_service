from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def return_book(self):
        if self.actual_return_date:
            raise ValidationError("This borrowing has already been returned.")

        self.actual_return_date = timezone.now().date()

        self.book.inventory += 1
        self.book.save()
        self.save()

    @staticmethod
    def validate_borrowing(book, error_to_raise):
        if book.inventory < 1:
            raise error_to_raise(
                {
                    "inventory": (
                        "Book inventory must be greater than or equal to 1 "
                        "to borrow the book."
                        f"(current inventory: {book.inventory})"
                    )
                }
            )

    def clean(self):
        if self.book:
            Borrowing.validate_borrowing(self.book, ValidationError)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
