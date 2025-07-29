import uuid
from django.utils.translation import gettext_lazy as _
from django.db import models
from freelancing.custom_auth.models import MerchantProfile, BaseModel, Category
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

# Create your models here.
class VoucherType(BaseModel):
    name = models.CharField("Voucher Type Name", max_length=100, unique=True)

    def __str__(self):
        return self.name

class Voucher(BaseModel):
    DEFAULT_TERMS = """Only one offer can be redeemed per transaction.
This offer is applicable once per user.
This offer can't be redeemed or clubbed with any other offers.
This offer is valid in select McDonald's (Hardcastle Restaurants) Branches in the West and South of India.
This offer is not applicable on delivery orders.
This offer cannot be replaced with cash.
This offer is valid while stocks lasts - McDonald's West and South (Hardcastle Restaurants Pvt. Ltd.) reserves the right to change the offers, menu and offers period any time without prior notice."""

    TYPE_PERCENTAGE = 'percentage'
    TYPE_FLAT = 'flat'
    TYPE_PRODUCT = 'product'
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
    merchant = models.ForeignKey(MerchantProfile, on_delete=models.CASCADE, related_name='vouchers')
    title = models.CharField("Title", max_length=255)
    message = models.TextField("Message")
    terms_conditions = models.TextField("Terms & Conditions", blank=True, default=DEFAULT_TERMS)
    count = models.PositiveIntegerField("Redemption Count", null=True, blank=True)
    image = models.ImageField(upload_to="vouchers/", null=True, blank=True)
    voucher_type = models.ForeignKey(VoucherType, on_delete=models.PROTECT, related_name='vouchers')

    # Type Specific Fields
    percentage_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    percentage_min_bill = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    flat_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    flat_min_bill = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    product_name = models.CharField(max_length=255, null=True, blank=True)
    product_min_bill = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='vouchers')
    redemption_count = models.PositiveIntegerField(default=0)
    
    is_gift_card = models.BooleanField(default=False)  # Hide from frontend listing

    def get_display_image(self):
        return self.image or self.merchant.banner_image

    def __str__(self):
        return f"{self.title} - {self.voucher_type.name}"

    class Meta:
        ordering = ['-create_time']


class Advertisement(BaseModel):
    voucher = models.OneToOneField(Voucher, on_delete=models.CASCADE, related_name="advertisement")
    banner_image = models.ImageField(upload_to="advertisements/")
    start_date = models.DateField()
    end_date = models.DateField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

    def clean(self):
        if not self.banner_image:
            raise ValidationError("Banner image is required to promote the voucher.")
    def __str__(self):
        return f"Ad: {self.voucher.title} in {self.city}, {self.state}"


class WhatsAppContact(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="whatsapp_contacts")
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    is_on_whatsapp = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({'✅' if self.is_on_whatsapp else '❌'})"

# class UserVoucherRedemption(BaseModel):
#     """Track which users redeemed which vouchers"""
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voucher_redemptions')
#     voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='user_redemptions')
#     redeemed_at = models.DateTimeField(auto_now_add=True)
#     is_gift_voucher = models.BooleanField(default=False)  # Track if it was a gift voucher redemption
   
#     class Meta:
#         unique_together = ['user', 'voucher']  # User can only redeem a voucher once
#         ordering = ['-redeemed_at']
   
#     def __str__(self):
#         return f"{self.user.fullname} redeemed {self.voucher.title}"
