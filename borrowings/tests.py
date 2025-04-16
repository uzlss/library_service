from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing


@patch("notifications.tasks.send_telegram_message_task.delay")
class BorrowingTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            email="admin@admin.com",
            password="<PASSWORD>",
            is_staff=True,
        )
        refresh = RefreshToken.for_user(self.admin_user)
        admin_access_token = str(refresh.access_token)
        self.admin_client = APIClient()
        self.admin_client.credentials(
            HTTP_AUTHORIZATION="Bearer " + admin_access_token
        )

        self.user1 = User.objects.create_user(
            email="user1@user.com",
            password="<PASSWORD>",
            is_staff=False,
        )
        refresh = RefreshToken.for_user(self.user1)
        user_access_token = str(refresh.access_token)
        self.user_client1 = APIClient()
        self.user_client1.credentials(
            HTTP_AUTHORIZATION="Bearer " + user_access_token
        )

        self.user2 = User.objects.create_user(
            email="user2@user.com",
            password="<PASSWORD>",
            is_staff=False
        )
        refresh = RefreshToken.for_user(self.user2)
        user_access_token = str(refresh.access_token)
        self.user_client2 = APIClient()
        self.user_client2.credentials(
            HTTP_AUTHORIZATION="Bearer " + user_access_token
        )

        self.book = Book.objects.create(
            title="Borrowing Book",
            author="Test Author",
            cover="HARD",
            inventory=10,
            daily_fee=Decimal("1.00"),
        )
        self.borrowing1 = Borrowing.objects.create(
            book=self.book,
            user=self.user1,
            expected_return_date=timezone.now().date(),
        )
        self.borrowing2 = Borrowing.objects.create(
            book=self.book,
            user=self.user2,
            expected_return_date=timezone.now().date(),
        )
        self.list_url = reverse("borrowings:borrowing-list")
        self.detail_url = reverse("borrowings:borrowing-detail", args=[self.borrowing1.id])

    def test_auth_required(self, mock_delay):
        list_response = self.client.get(self.list_url)

        detail_response = self.client.get(self.detail_url)

        create_data = {"book": self.book.id, "expected_return_date": timezone.now().date().isoformat()}
        create_response = self.client.post(self.list_url, create_data, content_type="application/json")

        for response in (list_response, detail_response, create_response):
            self.assertEqual(response.status_code, 401)

    def test_non_staff_can_see_only_their_borrowings(self, mock_delay):

        response = self.user_client1.get(self.list_url)
        self.assertEqual(response.status_code, 200)

        returned_ids = {item["id"] for item in response.json()}
        self.assertIn(self.borrowing1.id, returned_ids)
        self.assertNotIn(self.borrowing2.id, returned_ids)

        other_detail_url = reverse("borrowings:borrowing-detail", args=[self.borrowing2.id])
        detail_response = self.user_client1.get(other_detail_url)
        self.assertEqual(detail_response.status_code, 404)

    def test_staff_can_see_all_borrowings(self, mock_delay):
        response = self.admin_client.get(self.list_url)
        self.assertEqual(response.status_code, 200)

        borrowings = response.json()
        ids = [i["id"] for i in borrowings]
        self.assertIn(self.borrowing1.id, ids)
        self.assertIn(self.borrowing2.id, ids)

    def test_staff_can_filter_by_user_id(self, mock_delay):
        response = self.admin_client.get(self.list_url, {"user_id": self.user1.id})
        self.assertEqual(response.status_code, 200)

        filtered = response.json()
        for i in filtered:
            self.assertEqual(i.get("user"), self.user1.id)
        self.assertEqual({item["id"] for item in filtered}, {self.borrowing1.id})

    def test_is_active_filtering(self, mock_delay):
        self.borrowing1.actual_return_date = timezone.now().date()
        self.borrowing1.save()

        response = self.user_client1.get(self.list_url, {"is_active": True})
        filtered = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual({item["id"] for item in filtered}, {self.borrowing1.id})

        for item in filtered:
            borrowing_obj = Borrowing.objects.get(id=item["id"])
            self.assertIsNone(borrowing_obj.actual_return_date)

    def test_borrowings_decrease_book_inventory(self, mock_delay):
        inventory = self.book.inventory
        borrowing_data = {
            "book": self.book.id,
            "expected_return_date": (
                (timezone.now() + timezone.timedelta(days=1)
                 ).date()).isoformat(),
        }

        response = self.user_client1.post(self.list_url, borrowing_data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

        new_borrowing_id = response.json().get("id")
        new_borrowing = Borrowing.objects.get(id=new_borrowing_id)
        self.assertEqual(new_borrowing.user, self.user1)

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, inventory - 1)

    def test_cannot_create_borrowing_when_book_inventory_equal_to_0(self, mock_delay):
        self.book.inventory = 0
        self.book.save()
        borrowing_data = {
            "book": self.book.id,
            "expected_return_date": (
                (timezone.now() + timezone.timedelta(days=1)
                 ).date()).isoformat(),
        }
        response = self.user_client1.post(self.list_url, borrowing_data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        error = response.json()
        self.assertIn("inventory", error)

    def test_return_borrowing_endpoint(self, mock_delay):
        self.assertIsNone(self.borrowing1.actual_return_date)
        inventory = self.borrowing1.book.inventory

        return_url = reverse("borrowings:borrowing-return-borrowing", args=[self.borrowing1.id])
        response = self.user_client1.post(return_url, {})
        self.assertEqual(response.status_code, 200)

        self.borrowing1.refresh_from_db()
        self.assertIsNotNone(self.borrowing1.actual_return_date)
        self.assertEqual(self.borrowing1.book.inventory, inventory + 1)

        response = self.user_client1.post(return_url, {})
        self.assertEqual(response.status_code, 400)
        self.assertIn("This borrowing has already been returned.", str(response.json()))

        return_url = reverse("borrowings:borrowing-return-borrowing", args=[self.borrowing2.id])
        response = self.user_client1.post(return_url, {})
        self.assertNotEqual(response.status_code, 200)
