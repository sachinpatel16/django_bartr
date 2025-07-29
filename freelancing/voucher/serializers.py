from rest_framework import serializers
from freelancing.voucher.models import Voucher, VoucherType, WhatsAppContact, Advertisement
from freelancing.custom_auth.models import MerchantProfile, Category, Wallet, SiteSetting
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db import transaction
from phonenumber_field.serializerfields import PhoneNumberField

User = get_user_model()

class VoucherCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = [
            "id","merchant","category","title", "message", "terms_conditions", "count", "image", "voucher_type",
            "percentage_value", "percentage_min_bill",
            "flat_amount", "flat_min_bill",
            "product_name", "product_min_bill",
            "is_gift_card", "is_active"
        ]
        read_only_fields = ["id","merchant", "category"]

    def validate(self, data):
        """Validate voucher data based on voucher type"""
        voucher_type = data.get('voucher_type')
       
        if voucher_type.name == 'percentage':
            if not data.get('percentage_value'):
                raise serializers.ValidationError("Percentage value is required for percentage vouchers")
            if data.get('percentage_value') <= 0 or data.get('percentage_value') > 100:
                raise serializers.ValidationError("Percentage value must be between 0 and 100")
               
        elif voucher_type.name == 'flat':
            if not data.get('flat_amount'):
                raise serializers.ValidationError("Flat amount is required for flat vouchers")
            if data.get('flat_amount') <= 0:
                raise serializers.ValidationError("Flat amount must be greater than 0")
               
        elif voucher_type.name == 'product':
            if not data.get('product_name'):
                raise serializers.ValidationError("Product name is required for product vouchers")
               
        return data

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
       
        # Get merchant profile
        try:
            merchant_profile = MerchantProfile.objects.get(user=user)
        except MerchantProfile.DoesNotExist:
            raise serializers.ValidationError("Merchant profile not found for this user")
       
        validated_data["merchant"] = merchant_profile
        validated_data["category"] = merchant_profile.category

        # Determine cost
        is_gift_card = validated_data.get("is_gift_card", False)
        cost_key = "gift_card_cost" if is_gift_card else "voucher_cost"
        cost_value = Decimal(SiteSetting.get_value(cost_key, 10))

        # Get user's wallet (common wallet for both user and merchant)
        wallet = Wallet.objects.filter(user=user).first()
       
        if not wallet:
            raise serializers.ValidationError("User wallet not found.")

        # Check if user has sufficient balance
        if wallet.balance < cost_value:
            raise serializers.ValidationError(
                f"Insufficient balance. Required: ₹{cost_value}, Available: ₹{wallet.balance}"
            )

        # Deduct points from wallet
        try:
            wallet.deduct(cost_value, note="Voucher Creation", ref_id=str(validated_data.get("title")))
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

        # Create voucher
        voucher = super().create(validated_data)
        return voucher


class WhatsAppContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppContact
        fields = ['id', 'name', 'phone_number', 'is_on_whatsapp']
        read_only_fields = ['is_on_whatsapp']

    def validate_phone_number(self, value):
        """Validate phone number format"""
        if not value:
            raise serializers.ValidationError("Phone number is required")
        return value


class GiftCardShareSerializer(serializers.Serializer):
    phone_numbers = serializers.ListField(
        child=PhoneNumberField(),
        min_length=1,
        max_length=50,
        help_text="List of phone numbers to share gift card with"
    )

    def validate_phone_numbers(self, value):
        """Validate that phone numbers are unique"""
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate phone numbers are not allowed")
        return value


class AdvertisementSerializer(serializers.ModelSerializer):
    voucher_title = serializers.CharField(source='voucher.title', read_only=True)
    merchant_name = serializers.CharField(source='voucher.merchant.business_name', read_only=True)
   
    class Meta:
        model = Advertisement
        fields = [
            'id', 'voucher', 'voucher_title', 'merchant_name', 'banner_image',
            'start_date', 'end_date', 'city', 'state'
        ]
        read_only_fields = ['voucher_title', 'merchant_name']

    def validate(self, data):
        """Validate advertisement dates"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
       
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError("End date must be after start date")
       
        return data


