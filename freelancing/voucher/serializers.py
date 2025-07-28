from rest_framework import serializers
from freelancing.voucher.models import Voucher, VoucherType
from freelancing.custom_auth.models import MerchantProfile, Category, Wallet, SiteSetting
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

User = get_user_model()

class VoucherCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = [
            "merchant","category","title", "message", "terms_conditions", "count", "image", "voucher_type",
            "percentage_value", "percentage_min_bill",
            "flat_amount", "flat_min_bill",
            "product_name", "product_min_bill",
            "is_gift_card"
        ]
        read_only_fields = ["merchant", "category"]

    def create(self, validated_data):
        # user = self.context["request"].user.uuid
        request = self.context["request"]
        user = request.user
        # import pdb
        # pdb.set_trace()  # Debugging line to inspect user object
        user_uuid = user.uuid  # ✅ Get UUID without overwriting user
        merchant_id = MerchantProfile.objects.get(user=user)
        # import pdb
        # pdb.set_trace()
        # merchant = user.merchant_profile
        validated_data["merchant"] = merchant_id
        validated_data["category"] = merchant_id.category

        # Determine cost
        is_gift_card = validated_data.get("is_gift_card", False)
        cost_key = "gift_card_cost" if is_gift_card else "voucher_cost"
        cost_value = Decimal(SiteSetting.get_value(cost_key, 10))

        # Get wallet
        # user_uuid = User.objects.get(uuid=user_uuid)
        # import pdb
        # pdb.set_trace()
        wallet = Wallet.objects.filter(object_id=user_uuid).first()
        # wallet = Wallet.objects.filter(object_id=user_uuid.uuid, content_type=ContentType.objects.get_for_model(MerchantProfile)).first()
        if not wallet:
            raise serializers.ValidationError("Merchant wallet does not exist.")

        # Deduct points
        try:
            wallet.deduct(cost_value, note="Voucher Creation", ref_id=str(validated_data.get("title")))
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

        # Create voucher
        voucher = super().create(validated_data)
        return voucher

