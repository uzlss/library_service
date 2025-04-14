from django.db import models

from books_service.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True)
