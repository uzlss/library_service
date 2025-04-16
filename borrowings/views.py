from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer,
    BorrowingDetailSerializer,
    BorrowingAdminSerializer,
    BorrowingAdminDetailSerializer,
    BorrowingReturnSerializer,
)


class BorrowingViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    queryset = Borrowing.objects.all().prefetch_related("book")
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.request.user.is_staff:
            if self.action == "retrieve":
                return BorrowingAdminDetailSerializer
            if self.action == "list":
                return BorrowingAdminSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "return_borrowing":
            return BorrowingReturnSerializer
        return self.serializer_class

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset

        if user.is_staff:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user_id=user_id)
        else:
            queryset = queryset.filter(user=user)

        if self.request.query_params.get("is_active") in ("true", "True", "1"):
            queryset = queryset.filter(actual_return_date__isnull=True)

        return queryset.distinct()

    @action(detail=True, methods=["POST"], url_path="return")
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()

        if not request.user.is_staff and borrowing.user != request.user:
            return Response(
                {
                    "detail": "You do not have permission to return this borrowing."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(borrowing, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
