import uuid as uuid
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from django.core.exceptions import ValidationError
from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.authtoken.models import Token
# from tinymce.models import HTMLField

from freelancing.custom_auth.managers import ApplicationUserManager
from freelancing.custom_auth.mixins import UserPhotoMixin

from freelancing.utils.utils import set_otp_expiration_time, set_otp_reset_expiration_time


class MultiToken(Token):
    user = models.ForeignKey(  # changed from OneToOne to ForeignKey
        settings.AUTH_USER_MODEL,
        related_name="tokens",
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )


class CustomBlacklistedToken(models.Model):
    """
        Represent block access token of JWT
    """
    token = models.CharField(max_length=256, unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token


# Create your models here.
class BaseModel(models.Model):
    """This model is used for every model in same fields"""

    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ApplicationUser(AbstractBaseUser, UserPhotoMixin, PermissionsMixin):
    GENDER_TYPES = Choices(
        ("male", "Male"),
        ("female", "Female"),
        ("others", "Others"),
    )

    # uuid = universal unique identification
    username_validator = UnicodeUsernameValidator()
    uuid = models.UUIDField(
        verbose_name=_("uuid"),
        unique=True,
        help_text=_(
            "Required. A 32 hexadecimal digits number as specified in RFC 4122"
        ),
        error_messages={
            "unique": _("A user with that uuid already exists."),
        },
        default=uuid.uuid4,
    )

    username = models.CharField(
        _("username"),
        max_length=150,
        # unique=True,
        blank=True,
        null=False,  
        default="",
        help_text=(
            "Required. 150 characters or fewer. Lettres , digits and @/./+/-/ only ."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    email = models.EmailField(
        _("email address"),
        null=True,
        blank=True,
        unique=True,
        error_messages={"unique": _("A user with that email already exists.")},
    )

    is_email_verified = models.BooleanField(
        _("email verified"),
        default=False,
    )

    first_name = models.CharField(
        _("first name"),
        max_length=30,
        blank=True,
    )

    last_name = models.CharField(
        _("last name"),
        max_length=150,
        blank=True,
    )
    fullname = models.CharField(
        _("full name"),
        max_length=300,
        blank=True,
        help_text=_("Full name as it was returned by social provider"),
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether the user should be treated as active."
            "Unselect this instead of deleting account."
        ),
    )

    is_delete = models.BooleanField(
        _("delete"),
        default=False,
        help_text=_("Designates whether this user has been deleted."),
    )

    readable_password = models.CharField(max_length=128, null=True, blank=True)
    date_joined = models.DateTimeField(_("Registered date"), default=timezone.now)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True)
    last_user_activity = models.DateTimeField(_("last activity"), default=timezone.now)
    phone = PhoneNumberField(
        _("Mobile Number"),
        null=True,
        blank=True,
        unique=True,
        error_messages={"unique": _("A user with that phone already exists.")},
    )
    is_phone_verified = models.BooleanField(
        _("phone verified"),
        default=False,
    )
    gender = models.CharField(
        max_length=10, choices=GENDER_TYPES, null=True, blank=True
    )

    is_merchant = models.BooleanField(
        _('Is Merchant'),
        default=False,
        help_text=_('Designates whether the user is a merchant.'),
    )

    merchant_id = models.PositiveIntegerField(
        _('Merchant ID'),
        null=True,
        blank=True,
        help_text=_('Stores related MerchantProfile ID.')
    )

    address = models.TextField(_("Address"), null=True, blank=True)
    area = models.CharField(_("Area"), max_length=256, null=True, blank=True)
    pin = models.CharField(_("PIN Code"), max_length=10, null=True, blank=True)
    city = models.CharField(_("City"), max_length=100, null=True, blank=True)
    state = models.CharField(_("State"), max_length=100, null=True, blank=True)

    # address = models.TextField(_("Address"), null=True, blank=True)
    # partnership = models.BooleanField(default=False)
    # percentage = models.PositiveIntegerField(default=0)
    # assign_user_roll = models.ForeignKey("master.RollMaster", on_delete=models.PROTECT,
    #                                      related_name="user_roll_master_details", null=True, blank=True)

    # device address
    device_type = models.CharField(
        _("Device Type"), max_length=1, null=True, blank=True
    )
    device_token = models.CharField(
        _("Device Token"), max_length=256, null=True, blank=True
    )
    # device_id = models.CharField(_("Device Id"), max_length=256, null=True, blank=True)
    # os_version = models.CharField(_("OS Version"), max_length=8, null=True, blank=True)
    # device_name = models.CharField(
    #     _("Device Name"), max_length=64, null=True, blank=True
    # )
    # model_name = models.CharField(_("Model Name"), max_length=64, null=True, blank=True)
    # ip_address = models.CharField(_("IP Address"), max_length=32, null=True, blank=True)

    objects = ApplicationUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"  # email
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return str(self.phone) or str(self.email) or str(self.first_name) or str(self.last_name) or str(self.id)

    def save(self, *args, **kwargs):
        if self.photo and (not self.width_photo or not self.height_photo):
            self.width_photo = self.photo.width
            self.height_photo = self.photo.height

        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email)


        if self.fullname:
            self.assign_first_last_name_to_the_object()
        super(ApplicationUser, self).save(*args, **kwargs)

    def assign_first_last_name_to_the_object(self):
        if not self.fullname or not self.fullname.strip():
            return
            
        fullname_parts = self.fullname.strip().split(" ")
        # Filter out empty strings that might result from multiple spaces
        fullname_parts = [part for part in fullname_parts if part]
        
        if not fullname_parts:
            return
            
        self.first_name = fullname_parts[0]
        if len(fullname_parts) > 1:
            self.last_name = fullname_parts[1]
        else:
            self.last_name = fullname_parts[0]

    def update_last_activity(self):
        now = timezone.now()

        self.last_user_activity = now
        self.save(update_fields=("last_user_activity", "last_modified"))
    
    def clean(self):
        super().clean()
        if self.username is None:
            self.username = None  # ensure it's explicitly set

class Category(BaseModel):
    name = models.CharField(_("Category Name"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    image = models.ImageField(_("Category Image"), upload_to="categories/", null=True, blank=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['name']

    def __str__(self):
        return self.name
    
class MerchantProfile(BaseModel):
    user = models.OneToOneField(ApplicationUser, on_delete=models.CASCADE, related_name='merchant_profile')
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='merchants'
    )
    
    business_name = models.CharField(max_length=255)
    owner_name = models.CharField(_("Owner Name"), max_length=255, null=True, blank=True)
    email = models.EmailField(_("Merchant Email"), null=True, blank=True)
    phone = PhoneNumberField(_("Merchant Phone"), null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[("male", "Male"), ("female", "Female"), ("others", "Others")], null=True, blank=True)
    
    gst_number = models.CharField(max_length=20, null=True, blank=True)
    fssai_number = models.CharField(max_length=20, null=True, blank=True)
    
    address = models.TextField(_("Address"), null=True, blank=True)
    area = models.CharField(_("Area"), max_length=256, null=True, blank=True)
    pin = models.CharField(_("PIN Code"), max_length=10, null=True, blank=True)
    city = models.CharField(_("City"), max_length=100, null=True, blank=True)
    state = models.CharField(_("State"), max_length=100, null=True, blank=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    logo = models.ImageField(upload_to="merchant/logo/", null=True, blank=True)
    banner_image = models.ImageField(upload_to="merchant/banner/", null=True, blank=True)
    def __str__(self):
        return f"{self.business_name} ({self.user.email})"


class Wallet(BaseModel):
    user = models.OneToOneField(ApplicationUser, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # This is points balance

    def __str__(self):
        if self.user:
            return f"Wallet of {self.user.fullname} - {self.balance} points"
        else:
            return f"Orphaned Wallet - {self.balance} points"

    def deduct(self, amount: Decimal, note=None, ref_id=None):
        """Deduct points from wallet"""
        if self.balance < amount:
            raise ValidationError("Insufficient points in wallet.")
        self.balance -= amount
        self.save()
        WalletHistory.objects.create(
            wallet=self,
            amount=-amount,
            transaction_type='debit',
            reference_note=note,
            reference_id=ref_id
        )

    def credit(self, amount: Decimal, note=None, ref_id=None):
        """Add points to wallet"""
        self.balance += amount
        self.save()
        WalletHistory.objects.create(
            wallet=self,
            amount=amount,
            transaction_type='credit',
            reference_note=note,
            reference_id=ref_id
        )

    def add_points(self, points: Decimal, note=None, ref_id=None):
        """Add points to wallet (1 rupee = 10 points)"""
        self.credit(points, note, ref_id)

    def deduct_points(self, points: Decimal, note=None, ref_id=None):
        """Deduct points from wallet"""
        self.deduct(points, note, ref_id)
class WalletHistory(BaseModel):
    TRANSACTION_CHOICES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='histories')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference_note = models.CharField(max_length=255, null=True, blank=True)
    reference_id = models.CharField(max_length=100, null=True, blank=True)  # e.g. Voucher ID or Order ID
    meta = models.JSONField(null=True, blank=True) 
    def __str__(self):
        return f"{self.transaction_type.title()} ₹{self.amount}"


class RazorpayTransaction(BaseModel):
    """Model to store Razorpay payment transactions"""
    TRANSACTION_STATUS = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(ApplicationUser, on_delete=models.CASCADE, related_name='razorpay_transactions')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='razorpay_transactions')
    
    # Razorpay specific fields
    razorpay_order_id = models.CharField(max_length=255, unique=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    
    # Transaction details
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # Amount in rupees
    points_to_add = models.DecimalField(max_digits=12, decimal_places=2)  # Points to be added (1 rupee = 10 points)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending')
    
    # Additional details
    description = models.CharField(max_length=255, null=True, blank=True)
    receipt = models.CharField(max_length=255, null=True, blank=True)
    notes = models.JSONField(null=True, blank=True)
    
    # Error details
    error_code = models.CharField(max_length=100, null=True, blank=True)
    error_description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-create_time']

    def __str__(self):
        return f"Razorpay Transaction - {self.razorpay_order_id} - {self.status}"

    def mark_successful(self, payment_id, signature):
        """Mark transaction as successful and add points to wallet"""
        self.status = 'success'
        self.razorpay_payment_id = payment_id
        self.razorpay_signature = signature
        self.save()
        
        # Add points to wallet (1 rupee = 10 points)
        points_to_add = self.amount * 10  # 1 rupee = 10 points
        self.wallet.add_points(
            points_to_add,
            f"Razorpay payment - {self.razorpay_order_id}",
            self.razorpay_order_id
        )

    def mark_failed(self, error_code=None, error_description=None):
        """Mark transaction as failed"""
        self.status = 'failed'
        self.error_code = error_code
        self.error_description = error_description
        self.save()

class LoginOtp(BaseModel):
    """
        Represent check otp when you will login with phone number
    """
    user_mobile = PhoneNumberField()
    otp = models.IntegerField()
    expiration_time = models.DateTimeField(default=set_otp_reset_expiration_time)

    def save(self, *args, **kwargs):
        if not self.expiration_time:
            self.expiration_time = set_otp_expiration_time()
        return super().save()


class StudentOTP(BaseModel):
    email = models.EmailField(_("email"))
    otp = models.PositiveIntegerField(_("OTP"), null=True, blank=True)
    expiration_time = models.DateTimeField(default=set_otp_expiration_time)
    is_verified = models.BooleanField(default=0)

    def save(self, *args, **kwargs):
        self.expiration_time = set_otp_expiration_time()
        return super().save()


class UserActivity(models.Model):
    """
        It stores information about user activity
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_activity = models.DateTimeField(auto_now=True)


class CustomPermission(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    is_read_access = models.BooleanField(_("Read Access"), default=False)
    is_create_access = models.BooleanField(_("Create Access"), default=False)
    is_update_access = models.BooleanField(_("Update Access"), default=False)
    is_delete_access = models.BooleanField(_("Delete Access"), default=False)
    is_printed_access = models.BooleanField(_("Printed Access"), default=False)

    def __str__(self):
        return self.name


class SiteSetting(BaseModel):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.key}: {self.value}"

    @staticmethod
    def get_value(key, default=None):
        try:
            return SiteSetting.objects.get(key=key).value
        except SiteSetting.DoesNotExist:
            return default

class MerchantDeal(BaseModel):
    """Model for merchant deals with point-based system"""
    DEAL_STATUS = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('expired', 'Expired'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    merchant = models.ForeignKey(MerchantProfile, on_delete=models.CASCADE, related_name='deals_created')
    title = models.CharField(max_length=255)
    description = models.TextField()
    points_offered = models.DecimalField(max_digits=12, decimal_places=2)  # Points offered by merchant
    deal_value = models.DecimalField(max_digits=12, decimal_places=2)  # Actual value of deal
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=DEAL_STATUS, default='active')
    expiry_date = models.DateTimeField(null=True, blank=True)
    
    # Deal details
    points_used = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Points used from this deal
    points_remaining = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Remaining points
    
    # Location preferences
    preferred_cities = models.JSONField(default=list, blank=True)  # List of preferred cities
    preferred_categories = models.ManyToManyField(Category, related_name='preferred_deals', blank=True)
    
    # Deal terms
    terms_conditions = models.TextField(blank=True, null=True)
    is_negotiable = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        # Calculate remaining points
        self.points_remaining = self.points_offered - self.points_used
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-create_time']
    
    def __str__(self):
        return f"{self.merchant.business_name} - {self.title} ({self.points_required} points)"
    
    @property
    def is_expired(self):
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False


class MerchantDealRequest(BaseModel):
    """Model to track merchant deal requests"""
    REQUEST_STATUS = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )
    
    requesting_merchant = models.ForeignKey(MerchantProfile, on_delete=models.CASCADE, related_name='deal_requests_made')
    deal = models.ForeignKey(MerchantDeal, on_delete=models.CASCADE, related_name='deal_requests_received')
    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default='pending')
    request_time = models.DateTimeField(auto_now_add=True)
    
    # Request details
    message = models.TextField(blank=True, null=True)  # Merchant can add message
    points_requested = models.DecimalField(max_digits=12, decimal_places=2)  # Points requested
    counter_offer = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Counter offer points
    
    class Meta:
        unique_together = ('requesting_merchant', 'deal')  # One request per deal per merchant
        ordering = ['-request_time']
    
    def __str__(self):
        return f"{self.requesting_merchant.business_name} requests {self.deal.title} ({self.points_requested} points)"


class MerchantDealConfirmation(BaseModel):
    """Model for confirmed merchant deals"""
    CONFIRMATION_STATUS = (
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    deal_request = models.OneToOneField(MerchantDealRequest, on_delete=models.CASCADE, related_name='confirmation')
    deal = models.ForeignKey(MerchantDeal, on_delete=models.CASCADE, related_name='confirmations')
    merchant1 = models.ForeignKey(MerchantProfile, on_delete=models.CASCADE, related_name='deals_offered')
    merchant2 = models.ForeignKey(MerchantProfile, on_delete=models.CASCADE, related_name='deals_received')
    
    # Confirmation details
    status = models.CharField(max_length=20, choices=CONFIRMATION_STATUS, default='pending')
    confirmation_time = models.DateTimeField(null=True, blank=True)
    completed_time = models.DateTimeField(null=True, blank=True)
    
    # Deal terms
    points_exchanged = models.DecimalField(max_digits=12, decimal_places=2)  # Points exchanged
    deal_terms = models.TextField(blank=True, null=True)  # Agreed terms
    
    # Communication
    merchant1_notes = models.TextField(blank=True, null=True)
    merchant2_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-create_time']
    
    def __str__(self):
        return f"Deal: {self.merchant1.business_name} ↔ {self.merchant2.business_name} ({self.points_exchanged} points)"
    
    def confirm_deal(self):
        """Confirm the deal"""
        self.status = 'confirmed'
        self.confirmation_time = timezone.now()
        self.save()
    
    def complete_deal(self):
        """Mark deal as completed"""
        self.status = 'completed'
        self.completed_time = timezone.now()
        self.save()


class MerchantNotification(BaseModel):
    """Model for merchant notifications"""
    NOTIFICATION_TYPE = (
        ('deal_request', 'Deal Request'),
        ('deal_accepted', 'Deal Accepted'),
        ('deal_rejected', 'Deal Rejected'),
        ('deal_expired', 'Deal Expired'),
        ('points_transfer', 'Points Transfer'),
        ('system', 'System Notification'),
    )
    
    merchant = models.ForeignKey(MerchantProfile, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Related objects
    deal = models.ForeignKey(MerchantDeal, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    confirmation = models.ForeignKey(MerchantDealConfirmation, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    # Notification status
    is_read = models.BooleanField(default=False)
    read_time = models.DateTimeField(null=True, blank=True)
    
    # Action data
    action_url = models.CharField(max_length=500, blank=True, null=True)
    action_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-create_time']
    
    def __str__(self):
        return f"{self.merchant.business_name} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_time = timezone.now()
        self.save()


class DealPointUsage(BaseModel):
    """Model to track how deal points are used"""
    USAGE_TYPE = (
        ('exchange', 'Point Exchange'),
        ('discount', 'Discount Applied'),
        ('transfer', 'Point Transfer'),
    )
    
    deal = models.ForeignKey(MerchantDeal, on_delete=models.CASCADE, related_name='point_usages')
    confirmation = models.ForeignKey(MerchantDealConfirmation, on_delete=models.CASCADE, related_name='point_usages')
    from_merchant = models.ForeignKey(MerchantProfile, on_delete=models.CASCADE, related_name='points_used_from_deals')
    to_merchant = models.ForeignKey(MerchantProfile, on_delete=models.CASCADE, related_name='points_received_from_deals')
    
    # Usage details
    usage_type = models.CharField(max_length=20, choices=USAGE_TYPE)
    points_used = models.DecimalField(max_digits=12, decimal_places=2)
    usage_description = models.TextField(blank=True, null=True)
    
    # Transaction details
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    class Meta:
        ordering = ['-create_time']
    
    def __str__(self):
        return f"Deal Usage: {self.from_merchant.business_name} → {self.to_merchant.business_name}: {self.points_used} points"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"DEAL_USAGE_{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class MerchantPointsTransfer(BaseModel):
    """Model for points transfer between merchants after successful deals"""
    TRANSFER_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    confirmation = models.ForeignKey(MerchantDealConfirmation, on_delete=models.CASCADE, related_name='points_transfers')
    from_merchant = models.ForeignKey(MerchantProfile, on_delete=models.CASCADE, related_name='points_sent')
    to_merchant = models.ForeignKey(MerchantProfile, on_delete=models.CASCADE, related_name='points_received')
    
    # Transfer details
    points_amount = models.DecimalField(max_digits=12, decimal_places=2)
    transfer_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)  # points_amount - transfer_fee
    
    # Status and timing
    status = models.CharField(max_length=20, choices=TRANSFER_STATUS, default='pending')
    transfer_time = models.DateTimeField(null=True, blank=True)
    
    # Transaction details
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-create_time']
    
    def __str__(self):
        return f"{self.from_merchant.business_name} → {self.to_merchant.business_name}: {self.points_amount} points"
    
    def complete_transfer(self):
        """Complete the points transfer"""
        try:
            # Deduct points from sender
            self.from_merchant.user.wallet.deduct_points(
                self.points_amount,
                f"Transfer to {self.to_merchant.business_name}",
                self.transaction_id
            )
            
            # Add points to receiver
            self.to_merchant.user.wallet.add_points(
                self.net_amount,  # Net amount after fees
                f"Received from {self.from_merchant.business_name}",
                self.transaction_id
            )
            
            self.status = 'completed'
            self.transfer_time = timezone.now()
            self.save()
            
            return True
        except Exception as e:
            self.status = 'failed'
            self.notes = f"Transfer failed: {str(e)}"
            self.save()
            return False
