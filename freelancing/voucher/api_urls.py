from django.urls import include, path
from rest_framework import routers

from freelancing.voucher import api

router = routers.SimpleRouter()
router.register("v1/voucher", api.VoucherViewSet, basename="voucher")

app_name = "voucher"

urlpatterns = [
    # JWT Token Endpoints
    # path('v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("", include(router.urls))
]
