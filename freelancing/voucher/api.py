from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from freelancing.utils.permissions import IsAPIKEYAuthenticated

from freelancing.voucher.models import Voucher
from freelancing.voucher.serializers import VoucherCreateSerializer

class VoucherViewSet(viewsets.ModelViewSet):
    queryset = Voucher.objects.all()
    serializer_class = VoucherCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only show merchant's own vouchers
        return Voucher.objects.filter(merchant__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=["get"], url_path="popular", permission_classes=[permissions.AllowAny,
                                                                IsAPIKEYAuthenticated])
    def popular_vouchers(self, request):
        top_vouchers = Voucher.objects.filter(count__gt=0).order_by("-redemption_count")[:10]
        data = [{
            "id": v.id,
            "title": v.title,
            "merchant": v.merchant.business_name,
            "redemption_count": v.redemption_count
        } for v in top_vouchers]
        return Response(data)
