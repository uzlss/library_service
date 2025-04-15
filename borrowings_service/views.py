from rest_framework import viewsets, mixins

from borrowings_service.models import Borrowing
from borrowings_service.serializers import (
    BorrowingDetailSerializer,
    BorrowingSerializer,
    BorrowingCreateSerializer,
)


class BorrowingViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    queryset = Borrowing.objects.all().prefetch_related("book")
    serializer_class = BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset

        if self.request.user.is_staff:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = Borrowing.objects.filter(user_id=user_id)
        else:
            queryset = Borrowing.objects.filter(user=self.request.user)

        is_active = self.request.query_params.get("is_active")
        if is_active in ("true", "True", "1"):
            queryset = Borrowing.objects.filter(actual_return_date__isnull=True)

        return queryset.distinct()
