from django.contrib import admin
from django.db.models import BooleanField, Case, Value, When, Count, Sum, Avg
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models.functions import TruncDate

from freelancing.custom_auth.models import (ApplicationUser, MultiToken,
                                            UserActivity, CustomPermission,
                                            MerchantProfile, Wallet, Category, WalletHistory, SiteSetting, RazorpayTransaction,
                                            MerchantDeal, MerchantDealRequest, MerchantDealConfirmation, MerchantNotification, MerchantPointsTransfer, DealPointUsage)
from freelancing.voucher.models import Voucher

# Custom Admin Site Configuration
admin.site.site_header = "Bartr Admin Panel"
admin.site.site_title = "Bartr Administration"
admin.site.index_title = "Welcome to Bartr Administration"

# Custom ordering for admin models
# admin.site._registry = {}
# admin.site._registry_global = {}

# Register your models here.
# admin.site.register(MultiToken)
# admin.site.register()
# admin.site.register(UserActivity)
# admin.site.register(MerchantProfile)
# admin.site.register(Wallet)
# admin.site.register(Category)
# admin.site.register(WalletHistory)
# admin.site.register(SiteSetting)
# admin.site.register(RazorpayTransaction)

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone

User = get_user_model()


@admin.register(MultiToken)
class MultiTokenAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "MultiToken",
            {
                "fields": (
                    "user",
                    "key",
                    "created",
                )
            },
        ),
    )
    list_display = ("user", "key", "created")
    readonly_fields = ("user", "key", "created")
    search_fields = ("user__email", "user__fullname")


class VoucherInline(admin.TabularInline):
    model = Voucher
    extra = 0
    readonly_fields = ('uuid', 'purchase_count', 'redemption_count', 'redemption_rate')
    fields = ('title', 'voucher_type', 'is_active', 'is_gift_card', 'purchase_count', 'redemption_count', 'redemption_rate')
    can_delete = False
   
    def redemption_rate(self, obj):
        return f"{obj.get_redemption_rate()}%"
    redemption_rate.short_description = 'Redemption Rate'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image_preview', 'merchant_count', 'voucher_count')
    list_filter = ('is_active', 'create_time')
    search_fields = ('name', 'description')
    readonly_fields = ('merchant_count', 'voucher_count')
   
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'
   
    def merchant_count(self, obj):
        return obj.merchants.count()
    merchant_count.short_description = 'Merchants'
   
    def voucher_count(self, obj):
        return obj.vouchers.count()
    voucher_count.short_description = 'Vouchers'


@admin.register(MerchantProfile)
class MerchantProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'category', 'email', 'phone', 'city', 'state', 'voucher_count', 'is_active')
    list_filter = ('category', 'is_active', 'create_time', 'city', 'state')
    search_fields = ('business_name', 'user__email', 'user__fullname', 'gst_number', 'fssai_number')
    readonly_fields = ('voucher_count', 'logo_preview', 'banner_preview')
    actions = ['activate_merchants', 'deactivate_merchants']
    inlines = [VoucherInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'business_name', 'category', 'email', 'phone', 'gender')
        }),
        ('Business Details', {
            'fields': ('gst_number', 'fssai_number')
        }),
        ('Address Information', {
            'fields': ('address', 'area', 'pin', 'city', 'state')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Media', {
            'fields': ('logo', 'logo_preview', 'banner_image', 'banner_preview')
        }),
        ('Status', {
            'fields': ('is_active', 'is_delete')
        })
    )
   
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.logo.url)
        return "No Logo"
    logo_preview.short_description = 'Logo Preview'
   
    def banner_preview(self, obj):
        if obj.banner_image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 200px;" />', obj.banner_image.url)
        return "No Banner"
    banner_preview.short_description = 'Banner Preview'
   
    def voucher_count(self, obj):
        return obj.vouchers.count()
    voucher_count.short_description = 'Vouchers'
   
    def activate_merchants(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Successfully activated {updated} merchants.")
    activate_merchants.short_description = "Activate selected merchants"
   
    def deactivate_merchants(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Successfully deactivated {updated} merchants.")
    deactivate_merchants.short_description = "Deactivate selected merchants"


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'transaction_count', 'last_transaction_date')
    list_filter = ('is_active', 'create_time')
    search_fields = ('user__email', 'user__fullname')
    readonly_fields = ('transaction_count', 'last_transaction_date')
   
    def transaction_count(self, obj):
        return obj.histories.count()
    transaction_count.short_description = 'Transactions'
   
    def last_transaction_date(self, obj):
        last_transaction = obj.histories.order_by('-create_time').first()
        return last_transaction.create_time if last_transaction else "No transactions"
    last_transaction_date.short_description = 'Last Transaction'


@admin.register(WalletHistory)
class WalletHistoryAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'reference_note', 'reference_id', 'create_time')
    list_filter = ('transaction_type', 'create_time', 'is_active')
    search_fields = ('wallet__user__email', 'wallet__user__fullname', 'reference_note', 'reference_id')
    readonly_fields = ()
    date_hierarchy = 'create_time'


@admin.register(RazorpayTransaction)
class RazorpayTransactionAdmin(admin.ModelAdmin):
    list_display = ('razorpay_order_id', 'user', 'amount', 'points_to_add', 'status', 'create_time')
    list_filter = ('status', 'currency', 'create_time')
    search_fields = ('razorpay_order_id', 'razorpay_payment_id', 'user__email', 'user__fullname')
    readonly_fields = ('razorpay_order_id',)
    fieldsets = (
        ('Transaction Details', {
            'fields': ('user', 'wallet', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
        }),
        ('Amount Information', {
            'fields': ('amount', 'points_to_add', 'currency')
        }),
        ('Status & Description', {
            'fields': ('status', 'description', 'receipt', 'notes')
        }),
        ('Error Information', {
            'fields': ('error_code', 'error_description'),
            'classes': ('collapse',)
        })
    )
    date_hierarchy = 'create_time'


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'is_active', 'create_time')
    list_filter = ('is_active', 'create_time')
    search_fields = ('key', 'value')
    readonly_fields = ()


@admin.register(User)
class UserAdmin(UserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "phone", "password1", "password2"),
            },
        ),
    )
    fieldsets = (
        (
            "Personal info",
            {
                "fields": (
                    "uuid",
                    "username",
                    "first_name",
                    "last_name",
                    "fullname",
                    "email",
                    "phone",
                    "password",
                    "gender",
                    "address",
                    "area",
                    "pin",
                    "city",
                    "state",
                )
            },
        ),
        (
            "Statuses",
            {
                "fields": (
                    "is_active",
                    "is_email_verified",
                    "is_phone_verified",
                    "is_merchant",
                )
            },
        ),
        (
            "Service",
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Account dates",
            {
                "fields": (
                    "date_joined",
                    "last_login",
                    "last_user_activity",
                    "last_modified",
                )
            },
        ),
        ("Photo", {"fields": (("photo", "width_photo", "height_photo"),)}),
        ("Device Info", {
            "fields": ("device_type", "device_token"),
            "classes": ("collapse",)
        }),
    )
    readonly_fields = (
        "uuid",
        "last_name",
        "last_modified",
        "wallet_link",
        "merchant_profile_link",
    )
    list_display = (
        "phone",
        "username",
        "fullname",
        "email",
        "_get_password",
        "date_joined",
        "uuid",
        "last_user_activity",
        "is_staff",
        "is_superuser",
        "is_merchant",
        "wallet_balance",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "is_email_verified",
        "is_phone_verified",
        "is_merchant",
        "groups",
        "date_joined",
        "gender",
    )
    search_fields = ("username", "email", "uuid", "fullname", "phone")
    filter_horizontal = ("groups", "user_permissions")

    def _get_password(self, obj):
        return "Yes" if obj.password not in [None, ""] else "No"

    _get_password.short_description = "PASSWORD"
    _get_password.admin_order_field = "password"
   
    def wallet_link(self, obj):
        try:
            wallet = obj.wallet
            url = reverse('admin:custom_auth_wallet_change', args=[wallet.id])
            return format_html('<a href="{}">View Wallet (₹{})</a>', url, wallet.balance)
        except:
            return "No Wallet"
    wallet_link.short_description = "Wallet"
   
    def merchant_profile_link(self, obj):
        if obj.is_merchant:
            try:
                profile = obj.merchant_profile
                url = reverse('admin:custom_auth_merchantprofile_change', args=[profile.id])
                return format_html('<a href="{}">View Profile</a>', url)
            except:
                return "No Profile"
        return "Not a Merchant"
    merchant_profile_link.short_description = "Merchant Profile"
   
    def wallet_balance(self, obj):
        try:
            return f"₹{obj.wallet.balance}"
        except:
            return "₹0.00"
    wallet_balance.short_description = "Wallet Balance"

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        if search_term != "":
            queryset |= self.model.objects.filter(phone=search_term)

        return queryset, use_distinct

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                is_online=Case(
                    When(
                        last_user_activity__gte=timezone.now() - timedelta(minutes=5),
                        then=Value(True),
                    ),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
        )

    def is_online(self, obj):
        return obj.is_online

    is_online.boolean = True
    is_online.admin_order_field = "is_online"

# Merchant Deal System Admin
@admin.register(MerchantDeal)
class MerchantDealAdmin(admin.ModelAdmin):
    list_display = ['title', 'merchant', 'points_offered', 'points_used', 'points_remaining', 'deal_value', 'status', 'create_time']
    list_filter = ['status', 'category', 'create_time', 'expiry_date']
    search_fields = ['title', 'description', 'merchant__business_name']
    readonly_fields = ['points_used', 'points_remaining', 'create_time', 'update_time']
    list_editable = ['status']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('merchant', 'title', 'description', 'category')
        }),
        ('Deal Details', {
            'fields': ('points_offered', 'points_used', 'points_remaining', 'deal_value')
        }),
        ('Preferences', {
            'fields': ('preferred_cities', 'preferred_categories', 'terms_conditions', 'is_negotiable')
        }),
        ('Status & Timing', {
            'fields': ('status', 'expiry_date', 'create_time', 'update_time')
        }),
    )


@admin.register(MerchantDealRequest)
class MerchantDealRequestAdmin(admin.ModelAdmin):
    list_display = ['requesting_merchant', 'deal', 'status', 'points_requested', 'request_time']
    list_filter = ['status']
    search_fields = ['requesting_merchant__business_name', 'deal__title']
    readonly_fields = ['request_time']
    ordering = ['-request_time']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('requesting_merchant', 'deal', 'status')
        }),
        ('Request Details', {
            'fields': ('points_requested', 'counter_offer', 'message')
        }),
        ('Timing', {
            'fields': ('request_time',)
        }),
    )


@admin.register(MerchantDealConfirmation)
class MerchantDealConfirmationAdmin(admin.ModelAdmin):
    list_display = ['deal', 'merchant1', 'merchant2', 'status', 'points_exchanged', 'create_time']
    list_filter = ['status', 'create_time']
    search_fields = ['deal__title', 'merchant1__business_name', 'merchant2__business_name']
    readonly_fields = ['completed_time']
    ordering = ['-create_time']
    
    fieldsets = (
        ('Confirmation Information', {
            'fields': ('deal_request', 'deal', 'merchant1', 'merchant2', 'status')
        }),
        ('Deal Terms', {
            'fields': ('points_exchanged', 'deal_terms')
        }),
        ('Communication', {
            'fields': ('merchant1_notes', 'merchant2_notes')
        }),
        ('Timing', {
            'fields': ('confirmation_time', 'completed_time')
        }),
    )


@admin.register(DealPointUsage)
class DealPointUsageAdmin(admin.ModelAdmin):
    list_display = ['deal', 'from_merchant', 'to_merchant', 'usage_type', 'points_used', 'create_time']
    list_filter = ['usage_type']
    search_fields = ['deal__title', 'from_merchant__business_name', 'to_merchant__business_name', 'transaction_id']
    readonly_fields = ['transaction_id', 'create_time']
    ordering = ['-create_time']
    
    fieldsets = (
        ('Usage Information', {
            'fields': ('deal', 'confirmation', 'from_merchant', 'to_merchant')
        }),
        ('Usage Details', {
            'fields': ('usage_type', 'points_used', 'usage_description')
        }),
        ('Transaction', {
            'fields': ('transaction_id', 'create_time')
        }),
    )


@admin.register(MerchantNotification)
class MerchantNotificationAdmin(admin.ModelAdmin):
    list_display = ['merchant', 'notification_type', 'title', 'is_read', 'create_time']
    list_filter = ['notification_type', 'is_read', 'create_time']
    search_fields = ['merchant__business_name', 'title', 'message']
    readonly_fields = ['create_time', 'read_time']
    list_editable = ['is_read']


@admin.register(MerchantPointsTransfer)
class MerchantPointsTransferAdmin(admin.ModelAdmin):
    list_display = ['from_merchant', 'to_merchant', 'points_amount', 'status', 'transfer_time']
    list_filter = ['status', 'transfer_time']
    search_fields = ['from_merchant__business_name', 'to_merchant__business_name', 'transaction_id']
    readonly_fields = ['transfer_time', 'create_time']
    
    fieldsets = (
        ('Transfer Details', {
            'fields': ('confirmation', 'from_merchant', 'to_merchant', 'points_amount')
        }),
        ('Fees & Net Amount', {
            'fields': ('transfer_fee', 'net_amount')
        }),
        ('Status & Timing', {
            'fields': ('status', 'transfer_time', 'transaction_id')
        }),
        ('Additional Info', {
            'fields': ('notes', 'create_time')
        }),
    )
