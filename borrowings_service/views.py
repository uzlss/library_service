from rest_framework import viewsets, mixins

from borrowings_service.models import Borrowing
from borrowings_service.serializers import (
    BorrowingDetailSerializer,
    BorrowingSerializer,
)


class BorrowingViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    queryset = Borrowing.objects.all().prefetch_related("book")
    serializer_class = BorrowingSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return self.serializer_class
