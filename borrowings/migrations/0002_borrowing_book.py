# Generated by Django 5.2 on 2025-04-13 22:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0002_alter_book_inventory"),
        ("borrowings", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="borrowing",
            name="book",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="books.book",
            ),
        ),
    ]
