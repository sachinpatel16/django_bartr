from rest_framework import serializers
from freelancing.voucher.models import Voucher, VoucherType, WhatsAppContact, Advertisement, UserVoucherRedemption
from freelancing.custom_auth.models import MerchantProfile, Category, Wallet, SiteSetting
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db import transaction
from phonenumber_field.serializerfields import PhoneNumberField
from django.utils import timezone


User = get_user_model()

class VoucherTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoucherType
        fields = ['id', 'name']

class VoucherListSerializer(serializers.ModelSerializer):
    """Serializer for listing vouchers to users"""
    merchant_name = serializers.CharField(source='merchant.business_name', read_only=True)
    merchant_logo = serializers.SerializerMethodField()
    voucher_type_name = serializers.CharField(source='voucher_type.name', read_only=True)
    display_image = serializers.SerializerMethodField()
    voucher_value = serializers.SerializerMethodField()
    purchase_cost = serializers.SerializerMethodField()
    is_purchased = serializers.SerializerMethodField()
    can_purchase = serializers.SerializerMethodField()
    popularity_info = serializers.SerializerMethodField()
   
    class Meta:
        model = Voucher
        fields = [
            'id', 'uuid', 'title', 'message', 'merchant_name', 'merchant_logo', 'terms_conditions',
            'voucher_type_name', 'display_image', 'voucher_value', 'purchase_cost',
            'is_purchased', 'can_purchase', 'purchase_count', 'redemption_count', 'count',
            'percentage_value', 'percentage_min_bill', 'flat_amount', 'flat_min_bill',
            'product_name', 'product_min_bill', 'category', 'create_time', 'popularity_info'
        ]
   
    def get_merchant_logo(self, obj):
        if obj.merchant.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.merchant.logo.url)
            return obj.merchant.logo.url
        return None
   
    def get_display_image(self, obj):
        image = obj.get_display_image()
        if image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(image.url)
            return image.url
        return None
   
    def get_voucher_value(self, obj):
        """Get formatted voucher value based on type"""
        if obj.voucher_type.name == 'percentage':
            return f"{obj.percentage_value}% off"
        elif obj.voucher_type.name == 'flat':
            return f"₹{obj.flat_amount} off"
        elif obj.voucher_type.name == 'product':
            return f"Free {obj.product_name}"
        return "Special offer"
   
    def get_purchase_cost(self, obj):
        """Get cost to purchase this voucher"""
        try:
            is_gift_card = obj.is_gift_card
            cost_key = "gift_card_cost" if is_gift_card else "voucher_cost"
            voucher_cost_setting = SiteSetting.get_value(cost_key, "10")
            return Decimal(str(voucher_cost_setting))
        except (InvalidOperation, ValueError, TypeError):
            # If there's any issue with the setting, use default value
            return Decimal("10")
   
    def get_is_purchased(self, obj):
        """Check if current user has purchased this voucher"""
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return UserVoucherRedemption.objects.filter(
            user=user,
            voucher=obj,
            is_active=True
        ).exists()
   
    def get_can_purchase(self, obj):
        """Check if user can purchase this voucher"""
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
       
        # Check if already purchased
        if self.get_is_purchased(obj):
            return False
       
        # Check if voucher has reached its limit
        if obj.count and obj.redemption_count >= obj.count:
            return False
       
        # Check if user has sufficient wallet balance
        try:
            wallet = Wallet.objects.get(user=user)
            cost = self.get_purchase_cost(obj)
            return wallet.balance >= cost
        except Wallet.DoesNotExist:
            return False

    def get_popularity_info(self, obj):
        """Get popularity information for the voucher"""
        return {
            'purchase_count': obj.purchase_count,
            'redemption_count': obj.redemption_count,
            'popularity_score': obj.get_popularity_score(),
            'redemption_rate': obj.get_redemption_rate(),
            'is_popular': obj.purchase_count >= 10  # Consider popular if 10+ purchases
        }

class VoucherPurchaseSerializer(serializers.Serializer):
    """Serializer for purchasing vouchers with enhanced validation"""
    voucher_id = serializers.IntegerField()
   
    def validate_voucher_id(self, value):
        try:
            voucher = Voucher.objects.get(id=value, is_active=True)
            if voucher.is_gift_card:
                raise serializers.ValidationError("Gift cards cannot be purchased through this endpoint")
            return value
        except Voucher.DoesNotExist:
            raise serializers.ValidationError("Voucher not found or inactive")
        except Exception as e:
            raise serializers.ValidationError("Error validating voucher")
   
    def validate(self, data):
        user = self.context['request'].user
        voucher_id = data['voucher_id']
       
        try:
            voucher = Voucher.objects.get(id=voucher_id)
           
            # Check if already purchased
            if UserVoucherRedemption.objects.filter(user=user, voucher=voucher).exists():
                raise serializers.ValidationError("You have already purchased this voucher")
           
            # Check if voucher has reached its limit
            if voucher.count and voucher.redemption_count >= voucher.count:
                raise serializers.ValidationError("Voucher is out of stock")
           
            # Check wallet balance
            try:
                wallet = Wallet.objects.get(user=user)
                # Get voucher cost from settings with better error handling
                voucher_cost_setting = SiteSetting.get_value("voucher_cost", "10")
                cost = Decimal(str(voucher_cost_setting))
                if wallet.balance < cost:
                    raise serializers.ValidationError(
                        f"Insufficient balance. Required: ₹{cost}, Available: ₹{wallet.balance}"
                    )
            except Wallet.DoesNotExist:
                raise serializers.ValidationError("Wallet not found")
            except (InvalidOperation, ValueError, TypeError):
                # If there's any issue with the setting, use default value
                cost = Decimal("10")
                if wallet.balance < cost:
                    raise serializers.ValidationError(
                        f"Insufficient balance. Required: ₹{cost}, Available: ₹{wallet.balance}"
                    )
           
        except Voucher.DoesNotExist:
            raise serializers.ValidationError("Voucher not found")
        except Exception as e:
            raise serializers.ValidationError("Error validating purchase request")
       
        return data

class UserVoucherSerializer(serializers.ModelSerializer):
    """Serializer for user's purchased vouchers"""
    voucher_title = serializers.CharField(source='voucher.title', read_only=True)
    voucher_message = serializers.CharField(source='voucher.message', read_only=True)
    merchant_name = serializers.CharField(source='voucher.merchant.business_name', read_only=True)
    voucher_type = serializers.CharField(source='voucher.voucher_type.name', read_only=True)
    voucher_value = serializers.SerializerMethodField()
    display_image = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    can_redeem = serializers.SerializerMethodField()
   
    class Meta:
        model = UserVoucherRedemption
        fields = [
            'id', 'voucher', 'voucher_title', 'voucher_message', 'merchant_name',
            'voucher_type', 'voucher_value', 'display_image', 'purchased_at',
            'redeemed_at', 'is_active', 'purchase_cost', 'purchase_reference',
            'purchase_status', 'expiry_date', 'redemption_location', 'redemption_notes',
            'days_until_expiry', 'can_redeem'
        ]
   
    def get_voucher_value(self, obj):
        """Get formatted voucher value based on type"""
        voucher = obj.voucher
        if voucher.voucher_type.name == 'percentage':
            return f"{voucher.percentage_value}% off"
        elif voucher.voucher_type.name == 'flat':
            return f"₹{voucher.flat_amount} off"
        elif voucher.voucher_type.name == 'product':
            return f"Free {voucher.product_name}"
        return "Special offer"
   
    def get_display_image(self, obj):
        image = obj.voucher.get_display_image()
        if image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(image.url)
            return image.url
        return None

    def get_days_until_expiry(self, obj):
        """Calculate days until voucher expires"""
        if obj.expiry_date:
            from datetime import datetime
            now = timezone.now()
            delta = obj.expiry_date - now
            return max(0, delta.days)
        return None

    def get_can_redeem(self, obj):
        """Check if voucher can be redeemed"""
        return obj.can_redeem()

class VoucherRedeemSerializer(serializers.Serializer):
    """Serializer for redeeming vouchers with enhanced validation"""
    redemption_id = serializers.IntegerField()
    location = serializers.CharField(max_length=255, required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
   
    def validate_redemption_id(self, value):
        user = self.context['request'].user
        try:
            redemption = UserVoucherRedemption.objects.get(
                id=value,
                user=user
            )
            if not redemption.can_redeem():
                if redemption.is_expired():
                    raise serializers.ValidationError("Voucher has expired")
                elif redemption.redeemed_at:
                    raise serializers.ValidationError("Voucher has already been redeemed")
                else:
                    raise serializers.ValidationError("Voucher cannot be redeemed")
            return value
        except UserVoucherRedemption.DoesNotExist:
            raise serializers.ValidationError("Voucher not found or not purchased")
        except Exception as e:
            raise serializers.ValidationError("Error validating redemption")

class VoucherCancelSerializer(serializers.Serializer):
    """Serializer for cancelling voucher purchases with enhanced validation"""
    redemption_id = serializers.IntegerField()
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)
   
    def validate_redemption_id(self, value):
        user = self.context['request'].user
        try:
            redemption = UserVoucherRedemption.objects.get(
                id=value,
                user=user
            )
            if redemption.redeemed_at:
                raise serializers.ValidationError("Cannot cancel redeemed voucher")
            if redemption.purchase_status in ['cancelled', 'refunded']:
                raise serializers.ValidationError("Voucher is already cancelled or refunded")
            return value
        except UserVoucherRedemption.DoesNotExist:
            raise serializers.ValidationError("Voucher not found")
        except Exception as e:
            raise serializers.ValidationError("Error validating cancellation")

class VoucherRefundSerializer(serializers.Serializer):
    """Serializer for refunding voucher purchases with enhanced validation"""
    redemption_id = serializers.IntegerField()
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)
   
    def validate_redemption_id(self, value):
        user = self.context['request'].user
        try:
            redemption = UserVoucherRedemption.objects.get(
                id=value,
                user=user
            )
            if redemption.redeemed_at:
                raise serializers.ValidationError("Cannot refund redeemed voucher")
            if redemption.purchase_status in ['cancelled', 'refunded']:
                raise serializers.ValidationError("Voucher is already cancelled or refunded")
            return value
        except UserVoucherRedemption.DoesNotExist:
            raise serializers.ValidationError("Voucher not found")
        except Exception as e:
            raise serializers.ValidationError("Error validating refund")

class PurchaseHistorySerializer(serializers.ModelSerializer):
    """Serializer for detailed purchase history"""
    voucher_details = serializers.SerializerMethodField()
    merchant_details = serializers.SerializerMethodField()
   
    class Meta:
        model = UserVoucherRedemption
        fields = [
            'id', 'purchase_reference', 'purchase_status', 'purchased_at',
            'redeemed_at', 'expiry_date', 'purchase_cost', 'redemption_location',
            'redemption_notes', 'voucher_purchase_count', 'voucher_redemption_count', 
            'max_redemption_allowed', 'voucher_details', 'merchant_details'
        ]
   
    def get_voucher_details(self, obj):
        voucher = obj.voucher
        return {
            'id': voucher.id,
            'title': voucher.title,
            'message': voucher.message,
            'voucher_type': voucher.voucher_type.name,
            'image': self.get_voucher_image(voucher)
        }
   
    def get_merchant_details(self, obj):
        merchant = obj.voucher.merchant
        return {
            'id': merchant.id,
            'business_name': merchant.business_name,
            'logo': self.get_merchant_logo(merchant),
            'address': merchant.address,
            'city': merchant.city,
            'state': merchant.state
        }
   
    def get_voucher_image(self, voucher):
        image = voucher.get_display_image()
        if image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(image.url)
            return image.url
        return None
   
    def get_merchant_logo(self, merchant):
        if merchant.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(merchant.logo.url)
            return merchant.logo.url
        return None


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

        # Assign default terms and conditions if not provided
        if not validated_data.get('terms_conditions'):
            from freelancing.voucher.models import Voucher
            validated_data["terms_conditions"] = Voucher.DEFAULT_TERMS

        # Create voucher without deducting points from wallet
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


class MerchantVoucherScanSerializer(serializers.Serializer):
    """Serializer for merchant voucher scanning"""
    qr_data = serializers.CharField(
        max_length=100,
        help_text="QR code data (can be redemption ID, purchase reference, or voucher UUID)"
    )

class MerchantVoucherRedeemSerializer(serializers.Serializer):
    """Serializer for merchant voucher redemption"""
    redemption_id = serializers.IntegerField(
        help_text="ID of the voucher redemption record to redeem"
    )
    location = serializers.CharField(
        max_length=255,
        required=False,
        help_text="Location where voucher is being redeemed"
    )
    notes = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Additional notes about the redemption"
    )
    quantity = serializers.IntegerField(
        min_value=1,
        default=1,
        help_text="Number of vouchers to redeem from this purchase"
    )

    def validate_redemption_id(self, value):
        """Validate that redemption_id exists and is active"""
        try:
            redemption = UserVoucherRedemption.objects.get(
                id=value,
                is_active=True
            )
            return value
        except UserVoucherRedemption.DoesNotExist:
            raise serializers.ValidationError("Voucher redemption record not found or inactive")



