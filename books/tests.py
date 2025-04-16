from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient

from books.models import Book


class BookTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            email="admin@admin.com",
            password="<PASSWORD>",
            is_staff=True,
        )
        self.user = User.objects.create_user(
            email="user@user.com",
            password="<PASSWORD>",
            is_staff=False,
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=10,
            daily_fee=Decimal("1.00"),
        )
        self.new_book_data = {
            "title": "New Title",
            "author": "New Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": "1.00",
        }
        self.update_data = {"title": "Updated Title"}
        self.list_url = reverse("books:book-list")
        self.detail_url = reverse("books:book-detail", args=[self.book.id])

    def test_everyone_can_list_and_retrieve_books(self):
        list_response = self.client.get(self.list_url)
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, self.book.title)

        detail_response = self.client.get(self.detail_url)
        self.assertEqual(detail_response.status_code, 200)
        self.assertJSONEqual(
            detail_response.content.decode(),
            {
                "id": self.book.id,
                "title": "Test Book",
                "author": "Test Author",
                "cover": "HARD",
                "inventory": 10,
                "daily_fee": "1.00",
            },
        )

    def test_non_staff_user_cannot_create_update_delete_book(self):
        refresh = RefreshToken.for_user(self.user)
        user_access_token = str(refresh.access_token)
        user_client = APIClient()
        user_client.credentials(
            HTTP_AUTHORIZATION="Bearer " + user_access_token
        )

        create_response = user_client.post(
            self.list_url,
            data=self.new_book_data,
            content_type="application/json",
        )
        delete_response = user_client.delete(self.detail_url)
        update_response = user_client.patch(
            self.detail_url, self.update_data, content_type="application/json"
        )

        for response in (create_response, delete_response, update_response):
            self.assertEqual(response.status_code, 403)

    def test_staff_can_create_update_delete_book(self):
        refresh = RefreshToken.for_user(self.admin_user)
        admin_access_token = str(refresh.access_token)
        admin_client = APIClient()
        admin_client.credentials(
            HTTP_AUTHORIZATION="Bearer " + admin_access_token
        )

        response = admin_client.post(
            self.list_url, self.new_book_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        new_book = Book.objects.get(title="New Title")
        self.assertEqual(new_book.author, "New Author")
        self.assertEqual(new_book.daily_fee, Decimal("1.00"))

        detail_url_new = reverse("books:book-detail", args=[new_book.id])
        response = admin_client.patch(
            detail_url_new, self.update_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        new_book.refresh_from_db()
        self.assertEqual(new_book.title, "Updated Title")

        response = admin_client.delete(detail_url_new)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Book.objects.filter(id=new_book.id).exists())
