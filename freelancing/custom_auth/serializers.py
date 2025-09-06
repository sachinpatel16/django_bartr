import re
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from freelancing.custom_auth.models import (ApplicationUser, CustomPermission,
                                            MerchantProfile, Wallet,
                                            Category, WalletHistory, RazorpayTransaction,
                                            MerchantDeal, MerchantDealRequest, MerchantDealConfirmation, 
                                            MerchantNotification, MerchantPointsTransfer, DealPointUsage
                                        )
from freelancing.utils.validation import UniqueNameMixin

from freelancing.utils.email_send import Util

from django.template.loader import render_to_string
# reset password useing email
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError

User = get_user_model()


class UserAuthSerializer(serializers.Serializer):
    # LOGIN_TYPE = (
    #     ("S", _("Simple")),
    #     ("A", _("Apple")),
    #     ("F", _("Facebook")),
    #     ("G", _("Google")),
    # )

    # username = serializers.CharField(required=False)
    # email = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    # firebase_uid = serializers.CharField(required=False)
    # password = serializers.CharField(required=False)
    # login_type = serializers.ChoiceField(required=True, choices=LOGIN_TYPE)

    # LOGIN_TYPE_DICT = dict(LOGIN_TYPE)

    # def validate(self, attrs):
    #     login_type = attrs.get('login_type')
    #     email = attrs.get('email')
    #     phone = attrs.get('phone')
    #     password = attrs.get('password')
    #     firebase_uid = attrs.get('firebase_uid')

    #     if login_type in ['G', 'A', 'F'] and not firebase_uid:
    #         readable_login_type = self.LOGIN_TYPE_DICT[login_type]
    #         raise ValidationError(_("Enter firebase_uid for {} login").format(readable_login_type))

    #     elif not (email or phone or firebase_uid):
    #         raise ValidationError(_("Either email or phone should be provided"))

    #     elif email and not password:
    #         raise ValidationError(_("Enter password for email login"))

    #     elif password and not email:
    #         raise ValidationError(_("Enter email for password login"))

    #     elif phone:
    #         if not ApplicationUser.objects.filter(phone=phone).exists():
    #             raise ValidationError(_("Phone number doesn't exist"))

    #         elif not ApplicationUser.objects.filter(phone=phone, login_type=login_type).exists():
    #             raise ValidationError(_("Phone number doesn't exist with this login type"))

    #     return attrs
class BaseUserSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)
    # user_permission = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "uuid", "phone", "fullname", "first_name","last_name", "email", 
                    "photo", "gender", "is_merchant", "merchant_id", "address", "area", "pin", "city", "state",
                    "password", "is_active")
        read_only_fields = ("uuid",)
        ref_name = "BaseUserSerializer_ref"
        
    def get_photo(self, obj):
        try:
            photo = obj.photo
            if not photo:
                return None
            return UserPhotoSerializer(obj, context=self.context).data
        except Exception:
            return None




    def save(self, **kwargs):
        password = self.validated_data.pop("password", None)
        user = super().save(**kwargs)

        if password:
            user.set_password(password)
            user.save(update_fields=["password"])

        return user

class UserPhotoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    image = serializers.SerializerMethodField()
    width = serializers.ReadOnlyField(source="width_photo", allow_null=True)
    height = serializers.ReadOnlyField(source="height_photo", allow_null=True)

    class Meta:
        model = get_user_model()
        fields = ("id", "image", "width", "height")
        ref_name = 'UserPhotoSerializer_ref'
    
    def get_image(self, obj):
        try:
            if obj.photo:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.photo.url)
                return obj.photo.url
            return None
        except Exception:
            return None


class PasswordValidationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField()

    def validate_password(self, password):
        try:
            validate_password(password)
        except DjangoValidationError as ex:
            raise ValidationError(ex.messages)
        return password


class UserStatisticSerializerMixin:
    filters_amount = serializers.ReadOnlyField()

    class Meta:
        fields = ("filters_amount",)
        ref_name = "UserStatisticSerializerMixin_ref"


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        if validated_data["old_password"] == validated_data["new_password"]:
            raise ValidationError(
                _(
                    "Aww don't use the same password! For security reasons, please use a different "
                    "password to your old one"
                )
            )
        elif not self.context["request"].user.check_password(
            validated_data["old_password"]
        ):
            raise ValidationError(
                _("You've entered an incorrect old password, please try again.")
            )

        return validated_data


class CustomPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPermission
        fields = ['id', 'name', 'is_read_access', 'is_create_access', 'is_update_access',
                  'is_delete_access', 'is_printed_access']


class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ["email"]

    # def validate(self, attrs):
    #     email = attrs.get("email")
    #     if User.objects.filter(email=email).exists():
    #         user = User.objects.get(email=email)
    #         uid = urlsafe_base64_encode(force_bytes(user.id))
    #         print("Encoded uid: ", uid)
    #         token = PasswordResetTokenGenerator().make_token(user)
    #         print("Password reset token:", token)
    #         link = "http://127.0.0.1:8000/api/custom_auth/v1/user/reset/" + uid + "/" + token
    #         print("Password Reset Link", link)
    #         # Sent Email
    #         body = "Click Following Link to reset Passsword " + link
    #         data = {
    #             "subject": "Reset Your Password",
    #             "body": body,
    #             "to_email": user.email,
    #         }
    #         Util.send_mail(data)

    #         return attrs
    #     else:
    #         raise serializers.ValidationError("You are not a Register User!!")
    def validate(self, attrs):
        email = attrs.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            reset_link = f"http://localhost:5173/reset-password/{uid}/{token}"

            # Prepare context for the email template
            context = {
                "user": user,
                "reset_link": reset_link,
                "company_name": "Logo Inc",
                "support_email": "support@example.com",
            }

            # Render the email content
            html_content = render_to_string("../templates/password_reset_email.html", context)
            plain_text_content = f"Hi {user.username},\n\nClick the link below to reset your password:\n\n{reset_link}\n\nIf you did not request this, please ignore this email."

            data = {
                "subject": "Reset Your Password",
                "body_text": plain_text_content,  # Plain text body
                "body_html": html_content,  # HTML body
                "to_email": user.email,
            }
            Util.send_mail(data)
            return attrs
        else:
            raise serializers.ValidationError("You are not a registered user!")


class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        fields = ["password", "password2"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            password2 = attrs.get("password2")
            uid = self.context.get("uid")
            token = self.context.get("token")

            if password != password2:
                raise serializers.ValidationError(
                    "Password and Confirm Password doesn't match!!"
                )
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Token is not Valide or Expier")

            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError("Token is not Valide or Expier")

class CategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'image_url', 'is_active', 'create_time', 'update_time']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

def validate_gst_number(value):
    """Validate GST number format"""
    if not value:
        return value
   
    # GST number pattern: 2 digits + 10 digits + 1 digit + 1 digit
    gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
   
    if not re.match(gst_pattern, value.upper()):
        raise ValidationError(
            _('Invalid GST number format. Expected format: 22AAAAA0000A1Z5')
        )
    return value.upper()

def validate_fssai_number(value):
    """Validate FSSAI number format"""
    if not value:
        return value
   
    # FSSAI number pattern: 14 digits
    fssai_pattern = r'^[0-9]{14}$'
   
    if not re.match(fssai_pattern, value):
        raise ValidationError(
            _('Invalid FSSAI number format. Expected format: 14 digits')
        )
    return value

class MerchantProfileSerializer(serializers.ModelSerializer):
    gst_number = serializers.CharField(validators=[validate_gst_number], required=False, allow_blank=True)
    fssai_number = serializers.CharField(validators=[validate_fssai_number], required=False, allow_blank=True)
   
    class Meta:
        model = MerchantProfile
        fields = [
            'id', 'user', 'category', 'business_name', 'owner_name', 'email', 'phone', 'gender',
            'gst_number', 'fssai_number', 'address', 'area', 'pin', 'city', 'state',
            'latitude', 'longitude', 'logo', 'banner_image'
        ]
        read_only_fields = ['user']

    def validate(self, data):
        """Validate merchant profile data"""
        category = data.get('category')
        fssai_number = data.get('fssai_number')
       
        # Check if FSSAI is required for food category
        if category and category.name.lower() in ['food', 'restaurant', 'cafe', 'bakery']:
            if not fssai_number:
                raise serializers.ValidationError(
                    "FSSAI number is required for food-related businesses"
                )
       
        return data

class WalletSerializer(serializers.ModelSerializer):
    # user_name = serializers.CharField(source='user.fullname', read_only=True)
    # user_email = serializers.CharField(source='user.email', read_only=True)
   
    class Meta:
        model = Wallet
        fields = [
            'id', 'user', 'balance',
            'is_active', 'create_time', 'update_time'
        ]
        read_only_fields = ['id', 'create_time', 'update_time']

class WalletHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletHistory
        fields = [
            "id", "transaction_type", "amount", "reference_note", "reference_id", "meta", 'create_time'
            ]


class MerchantListingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.fullname', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_image = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    banner_url = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    available_vouchers_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = MerchantProfile
        fields = [
            'id', 'user', 'user_name', 'user_email', 'user_phone', 'category', 'category_name',
            'category_image', 'business_name', 'owner_name', 'email', 'phone', 'gender', 'gst_number',
            'fssai_number', 'address', 'area', 'pin', 'city', 'state', 'latitude', 'longitude',
            'logo', 'logo_url', 'banner_image', 'banner_url', 'distance', 'available_vouchers_count', 'is_active',
            'create_time', 'update_time'
        ]
        read_only_fields = ['user', 'user_name', 'user_email', 'user_phone', 'category_name',
                            'category_image', 'logo_url', 'banner_url', 'distance', 'available_vouchers_count']
   
    def get_category_image(self, obj):
        if obj.category and obj.category.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.category.image.url)
            return obj.category.image.url
        return None
   
    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None
   
    def get_banner_url(self, obj):
        if obj.banner_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.banner_image.url)
            return obj.banner_image.url
        return None
   
    def get_distance(self, obj):
        # This can be calculated based on user's location if provided
        # For now, returning None - can be implemented later
        return None


class RazorpayOrderSerializer(serializers.Serializer):
    """Serializer for creating Razorpay order"""
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('1.0'))
    currency = serializers.CharField(default='INR', max_length=3)
    description = serializers.CharField(max_length=255, required=False, allow_blank=True)
    receipt = serializers.CharField(max_length=255, required=False, allow_blank=True)
    notes = serializers.JSONField(required=False)

    def validate_amount(self, value):
        """Validate amount and ensure it's at least 1 rupee (1 rupee = 10 points)"""
        if value < 1:
            raise serializers.ValidationError("Amount must be at least ₹1")
        return value


class RazorpayPaymentVerificationSerializer(serializers.Serializer):
    """Serializer for verifying Razorpay payment"""
    razorpay_order_id = serializers.CharField(max_length=255)
    razorpay_payment_id = serializers.CharField(max_length=255)
    razorpay_signature = serializers.CharField(max_length=255, required=False, allow_blank=True)


class RazorpayTransactionSerializer(serializers.ModelSerializer):
    """Serializer for Razorpay transaction model"""
    user_name = serializers.CharField(source='user.fullname', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = RazorpayTransaction
        fields = [
            'id', 'user', 'user_name', 'user_email', 'wallet', 'razorpay_order_id',
            'razorpay_payment_id', 'razorpay_signature', 'amount', 'points_to_add',
            'currency', 'status', 'description', 'receipt', 'notes', 'error_code',
            'error_description', 'create_time', 'update_time'
        ]
        read_only_fields = [
            'id', 'user', 'user_name', 'user_email', 'wallet', 'razorpay_order_id',
            'razorpay_payment_id', 'razorpay_signature', 'points_to_add', 'status',
            'error_code', 'error_description', 'create_time', 'update_time'
        ]

# Merchant Deal System Serializers
class MerchantDealSerializer(serializers.ModelSerializer):
    merchant_name = serializers.CharField(source='merchant.business_name', read_only=True)
    merchant_logo = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    request_count = serializers.SerializerMethodField()
    confirmation_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MerchantDeal
        fields = [
            'id', 'merchant', 'merchant_name', 'merchant_logo', 'title', 'description',
            'points_offered', 'points_used', 'points_remaining', 'deal_value', 'category', 
            'category_name', 'status', 'expiry_date', 'is_expired', 'preferred_cities',
            'preferred_categories', 'terms_conditions', 'is_negotiable', 'request_count',
            'confirmation_count', 'create_time'
        ]
        read_only_fields = ['merchant', 'points_used', 'points_remaining', 'create_time']
    
    def get_merchant_logo(self, obj):
        if obj.merchant.logo:
            return self.context['request'].build_absolute_uri(obj.merchant.logo.url)
        return None
    
    def get_request_count(self, obj):
        return obj.deal_requests_received.count()
    
    def get_confirmation_count(self, obj):
        return obj.confirmations.filter(status='confirmed').count()
    
    def validate(self, data):
        if data.get('expiry_date') and data['expiry_date'] <= timezone.now():
            raise serializers.ValidationError("Expiry date must be in the future")
        
        return data


class MerchantDealCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantDeal
        fields = [
            'title', 'description', 'points_offered', 'deal_value', 'category',
            'expiry_date', 'preferred_cities', 'preferred_categories', 
            'terms_conditions', 'is_negotiable'
        ]
    
    def validate_points_offered(self, value):
        """Validate that merchant has enough points in wallet"""
        user = self.context['request'].user
        if hasattr(user, 'wallet'):
            if user.wallet.balance < value:
                raise serializers.ValidationError(
                    f"Insufficient points in wallet. Available: {user.wallet.balance}, Required: {value}"
                )
        else:
            raise serializers.ValidationError("Wallet not found for user")
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['merchant'] = user.merchant_profile
        
        # Deduct points from wallet when deal is created
        points_offered = validated_data['points_offered']
        user.wallet.deduct_points(
            points_offered,
            f"Deal created: {validated_data['title']}",
            f"DEAL_{uuid.uuid4().hex[:8].upper()}"
        )
        
        return super().create(validated_data)


class MerchantDealRequestSerializer(serializers.ModelSerializer):
    requesting_merchant_name = serializers.CharField(source='requesting_merchant.business_name', read_only=True)
    deal_title = serializers.CharField(source='deal.title', read_only=True)
    deal_merchant = serializers.CharField(source='deal.merchant.business_name', read_only=True)
    
    class Meta:
        model = MerchantDealRequest
        fields = [
            'id', 'requesting_merchant', 'requesting_merchant_name', 'deal', 'deal_title', 
            'deal_merchant', 'status', 'request_time', 'message', 'points_requested', 'counter_offer'
        ]
        read_only_fields = ['requesting_merchant', 'request_time']
    
    def validate(self, data):
        # Check if merchant is requesting their own deal
        if data['deal'].merchant == data['requesting_merchant']:
            raise serializers.ValidationError("You cannot request your own deal")
        
        # Check if already requested
        if MerchantDealRequest.objects.filter(
            requesting_merchant=data['requesting_merchant'], 
            deal=data['deal']
        ).exists():
            raise serializers.ValidationError("You have already requested this deal")
        
        # Check if deal has enough remaining points
        if data['points_requested'] > data['deal'].points_remaining:
            raise serializers.ValidationError(
                f"Requested points ({data['points_requested']}) exceed available points ({data['deal'].points_remaining})"
            )
        
        return data


class MerchantDealConfirmationSerializer(serializers.ModelSerializer):
    deal_title = serializers.CharField(source='deal.title', read_only=True)
    merchant1_name = serializers.CharField(source='merchant1.business_name', read_only=True)
    merchant2_name = serializers.CharField(source='merchant2.business_name', read_only=True)
    merchant1_logo = serializers.SerializerMethodField()
    merchant2_logo = serializers.SerializerMethodField()
    
    class Meta:
        model = MerchantDealConfirmation
        fields = [
            'id', 'deal', 'deal_title', 'merchant1', 'merchant1_name', 'merchant1_logo',
            'merchant2', 'merchant2_name', 'merchant2_logo', 'status', 'confirmation_time',
            'completed_time', 'points_exchanged', 'deal_terms',
            'merchant1_notes', 'merchant2_notes'
        ]
        read_only_fields = ['confirmation_time']
    
    def get_merchant1_logo(self, obj):
        if obj.merchant1.logo:
            return self.context['request'].build_absolute_uri(obj.merchant1.logo.url)
        return None
    
    def get_merchant2_logo(self, obj):
        if obj.merchant2.logo:
            return self.context['request'].build_absolute_uri(obj.merchant2.logo.url)
        return None




class MerchantNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantNotification
        fields = [
            'id', 'notification_type', 'title', 'message', 'deal', 'match',
            'is_read', 'read_time', 'action_url', 'action_data', 'create_time'
        ]
        read_only_fields = ['create_time']


class MerchantPointsTransferSerializer(serializers.ModelSerializer):
    from_merchant_name = serializers.CharField(source='from_merchant.business_name', read_only=True)
    to_merchant_name = serializers.CharField(source='to_merchant.business_name', read_only=True)
    
    class Meta:
        model = MerchantPointsTransfer
        fields = [
            'id', 'match', 'from_merchant', 'from_merchant_name', 'to_merchant',
            'to_merchant_name', 'points_amount', 'transfer_fee', 'net_amount',
            'status', 'transfer_time', 'transaction_id', 'notes', 'create_time'
        ]
        read_only_fields = ['transfer_time', 'create_time']


class DealDiscoverySerializer(serializers.Serializer):
    """Serializer for deal discovery with filters"""
    category = serializers.IntegerField(required=False)
    min_points = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    max_points = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    city = serializers.CharField(required=False)
    search_query = serializers.CharField(required=False)
    page = serializers.IntegerField(default=1)
    page_size = serializers.IntegerField(default=20)


class DealPointUsageSerializer(serializers.ModelSerializer):
    deal_title = serializers.CharField(source='deal.title', read_only=True)
    from_merchant_name = serializers.CharField(source='from_merchant.business_name', read_only=True)
    to_merchant_name = serializers.CharField(source='to_merchant.business_name', read_only=True)
    
    class Meta:
        model = DealPointUsage
        fields = [
            'id', 'deal', 'deal_title', 'confirmation', 'from_merchant', 'from_merchant_name',
            'to_merchant', 'to_merchant_name', 'usage_type', 'points_used', 
            'usage_description', 'transaction_id', 'create_time'
        ]
        read_only_fields = ['transaction_id', 'create_time']


class DealStatsSerializer(serializers.Serializer):
    """Serializer for deal statistics"""
    total_deals = serializers.IntegerField()
    active_deals = serializers.IntegerField()
    total_requests = serializers.IntegerField()
    successful_deals = serializers.IntegerField()
    total_points_offered = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_points_used = serializers.DecimalField(max_digits=12, decimal_places=2)
