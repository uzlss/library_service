from django.core.exceptions import ValidationError
from django.db import models

from books_service.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True)

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
