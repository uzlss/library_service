from django.core.validators import MinValueValidator
from django.db import models


class Book(models.Model):

    class Cover(models.TextChoices):
        HARD = "HARD"
        SOFT = "SOFT"

    title = models.CharField(max_length=255, unique=True)
    author = models.CharField(max_length=255)
    cover = models.CharField(choices=Cover.choices, max_length=50)
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2)  # $USD
