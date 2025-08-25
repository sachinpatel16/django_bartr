from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta

# Register your models here.

from freelancing.voucher.models import Voucher, VoucherType, UserVoucherRedemption, Advertisement, WhatsAppContact, GiftCardShare


@admin.register(VoucherType)
class VoucherTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'voucher_count', 'is_active', 'create_time')
    list_filter = ('is_active', 'create_time')
    search_fields = ('name',)
    readonly_fields = ('voucher_count',)
   
    def voucher_count(self, obj):
        return obj.vouchers.count()
    voucher_count.short_description = 'Vouchers'


class AdvertisementInline(admin.TabularInline):
    model = Advertisement
    extra = 0
    fields = ('banner_image', 'start_date', 'end_date', 'city', 'state', 'is_active')


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('title', 'merchant', 'voucher_type', 'get_discount_display', 'purchase_count', 'redemption_count', 'redemption_rate', 'is_active', 'is_gift_card')
    list_filter = ('voucher_type', 'merchant__category', 'is_active', 'is_gift_card', 'create_time', 'merchant__city', 'merchant__state')
    search_fields = ('title', 'message', 'merchant__business_name', 'merchant__user__email')
    readonly_fields = ('uuid', 'purchase_count', 'redemption_count', 'redemption_rate', 'popularity_score', 'image_preview')
    date_hierarchy = 'create_time'
    actions = ['make_active', 'make_inactive', 'make_gift_card', 'remove_gift_card']
   
    fieldsets = (
        ('Basic Information', {
            'fields': ('uuid', 'merchant', 'title', 'message', 'voucher_type', 'category')
        }),
        ('Voucher Details', {
            'fields': ('terms_conditions', 'count', 'image', 'image_preview')
        }),
        ('Discount Configuration', {
            'fields': (
                'percentage_value', 'percentage_min_bill',
                'flat_amount', 'flat_min_bill',
                'product_name', 'product_min_bill'
            )
        }),
        ('Statistics', {
            'fields': ('purchase_count', 'redemption_count', 'redemption_rate', 'popularity_score'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_gift_card', 'is_active', 'is_delete')
        })
    )
   
    inlines = [AdvertisementInline]
   
    def get_discount_display(self, obj):
        if obj.voucher_type.name == 'Percentage':
            return f"{obj.percentage_value}% off (min ₹{obj.percentage_min_bill})"
        elif obj.voucher_type.name == 'Flat':
            return f"₹{obj.flat_amount} off (min ₹{obj.flat_min_bill})"
        elif obj.voucher_type.name == 'Product':
            return f"{obj.product_name} (min ₹{obj.product_min_bill})"
        return "N/A"
    get_discount_display.short_description = 'Discount'
   
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 200px;" />', obj.image.url)
        elif obj.merchant.banner_image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 200px;" />', obj.merchant.banner_image.url)
        return "No Image"
    image_preview.short_description = 'Image Preview'
   
    def redemption_rate(self, obj):
        return f"{obj.get_redemption_rate()}%"
    redemption_rate.short_description = 'Redemption Rate'
   
    def popularity_score(self, obj):
        return obj.get_popularity_score()
    popularity_score.short_description = 'Popularity Score'
   
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('merchant', 'merchant__user', 'voucher_type', 'category')
   
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Successfully activated {updated} vouchers.")
    make_active.short_description = "Activate selected vouchers"
   
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Successfully deactivated {updated} vouchers.")
    make_inactive.short_description = "Deactivate selected vouchers"
   
    def make_gift_card(self, request, queryset):
        updated = queryset.update(is_gift_card=True)
        self.message_user(request, f"Successfully marked {updated} vouchers as gift cards.")
    make_gift_card.short_description = "Mark selected vouchers as gift cards"
   
    def remove_gift_card(self, request, queryset):
        updated = queryset.update(is_gift_card=False)
        self.message_user(request, f"Successfully removed gift card status from {updated} vouchers.")
    remove_gift_card.short_description = "Remove gift card status from selected vouchers"


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('voucher', 'merchant_name', 'city', 'state', 'start_date', 'end_date', 'is_active', 'days_remaining')
    list_filter = ('city', 'state', 'is_active', 'start_date', 'end_date')
    search_fields = ('voucher__title', 'voucher__merchant__business_name', 'city', 'state')
    readonly_fields = ('days_remaining', 'banner_preview')
    date_hierarchy = 'start_date'
   
    fieldsets = (
        ('Voucher Information', {
            'fields': ('voucher',)
        }),
        ('Advertisement Details', {
            'fields': ('banner_image', 'banner_preview', 'start_date', 'end_date')
        }),
        ('Location', {
            'fields': ('city', 'state')
        }),
        ('Status', {
            'fields': ('is_active', 'is_delete')
        })
    )
   
    def merchant_name(self, obj):
        return obj.voucher.merchant.business_name
    merchant_name.short_description = 'Merchant'
   
    def banner_preview(self, obj):
        if obj.banner_image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 200px;" />', obj.banner_image.url)
        return "No Banner"
    banner_preview.short_description = 'Banner Preview'
   
    def days_remaining(self, obj):
        if obj.end_date:
            remaining = obj.end_date - timezone.now().date()
            if remaining.days > 0:
                return f"{remaining.days} days"
            elif remaining.days == 0:
                return "Today"
            else:
                return f"Expired ({abs(remaining.days)} days ago)"
        return "No end date"
    days_remaining.short_description = 'Days Remaining'


@admin.register(WhatsAppContact)
class WhatsAppContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'phone_number', 'is_on_whatsapp', 'create_time')
    list_filter = ('is_on_whatsapp', 'create_time')
    search_fields = ('name', 'phone_number', 'user__email', 'user__fullname')


class UserVoucherRedemptionInline(admin.TabularInline):
    model = UserVoucherRedemption
    extra = 0
    readonly_fields = ('purchased_at', 'redeemed_at', 'purchase_reference', 'expiry_date')
    fields = ('user', 'purchased_at', 'redeemed_at', 'purchase_status', 'is_active', 'purchase_cost')
    can_delete = False


@admin.register(UserVoucherRedemption)
class UserVoucherRedemptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'voucher', 'merchant_name', 'purchase_status', 'purchase_cost', 'purchased_at', 'redeemed_at', 'days_remaining', 'is_active')
    list_filter = ('purchase_status', 'is_gift_voucher', 'is_active', 'purchased_at', 'redeemed_at', 'voucher__merchant__category')
    search_fields = ('user__email', 'user__fullname', 'voucher__title', 'voucher__merchant__business_name', 'purchase_reference')
    readonly_fields = ('purchase_reference', 'purchased_at', 'redeemed_at', 'expiry_date', 'days_remaining', 'wallet_transaction_link')
    date_hierarchy = 'purchased_at'
   
    fieldsets = (
        ('Purchase Information', {
            'fields': ('user', 'voucher', 'purchase_reference', 'purchase_cost', 'purchased_at')
        }),
        ('Redemption Details', {
            'fields': ('redeemed_at', 'redemption_location', 'redemption_notes', 'purchase_status')
        }),
        ('Voucher Status', {
            'fields': ('is_active', 'is_gift_voucher', 'expiry_date', 'days_remaining')
        }),
        ('Wallet Transaction', {
            'fields': ('wallet_transaction_id', 'wallet_transaction_link'),
            'classes': ('collapse',)
        })
    )
   
    actions = ['bulk_expire_vouchers', 'mark_as_redeemed']
   
    def merchant_name(self, obj):
        return obj.voucher.merchant.business_name
    merchant_name.short_description = 'Merchant'
   
    def days_remaining(self, obj):
        return obj.get_remaining_days()
    days_remaining.short_description = 'Days Remaining'
   
    def wallet_transaction_link(self, obj):
        if obj.wallet_transaction_id:
            return format_html('<a href="{}">View Transaction</a>',
                             reverse('admin:custom_auth_wallethistory_changelist') + f'?reference_id={obj.wallet_transaction_id}')
        return "No Transaction"
    wallet_transaction_link.short_description = 'Wallet Transaction'
   
    def bulk_expire_vouchers(self, request, queryset):
        count = 0
        for redemption in queryset:
            if redemption.can_redeem() and redemption.is_expired():
                redemption.purchase_status = 'expired'
                redemption.is_active = False
                redemption.redemption_notes = f"Bulk expired by admin on {timezone.now()}"
                redemption.save()
                count += 1
        self.message_user(request, f"Successfully expired {count} vouchers.")
    bulk_expire_vouchers.short_description = "Expire selected vouchers"
   
    def mark_as_redeemed(self, request, queryset):
        count = 0
        for redemption in queryset:
            if redemption.can_redeem():
                redemption.redeem(location="Admin Panel", notes="Marked as redeemed by admin")
                count += 1
        self.message_user(request, f"Successfully marked {count} vouchers as redeemed.")
    mark_as_redeemed.short_description = "Mark selected vouchers as redeemed"
   
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'voucher', 'voucher__merchant', 'voucher__merchant__user'
        )


@admin.register(GiftCardShare)
class GiftCardShareAdmin(admin.ModelAdmin):
    list_display = ('original_purchase', 'recipient_phone', 'recipient_name', 'shared_via', 'is_claimed', 'claimed_by_user', 'create_time')
    list_filter = ('shared_via', 'is_claimed', 'create_time', 'claimed_at')
    search_fields = ('recipient_phone', 'recipient_name', 'original_purchase__voucher__title', 'original_purchase__user__email')
    readonly_fields = ('claim_reference', 'create_time', 'claimed_at', 'original_purchase_details')
    date_hierarchy = 'create_time'
    
    fieldsets = (
        ('Gift Card Information', {
            'fields': ('original_purchase', 'original_purchase_details')
        }),
        ('Recipient Details', {
            'fields': ('recipient_phone', 'recipient_name', 'shared_via')
        }),
        ('Claim Status', {
            'fields': ('is_claimed', 'claimed_at', 'claimed_by_user', 'claim_reference')
        }),
        ('System Information', {
            'fields': ('create_time', 'is_active', 'is_delete'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_claimed', 'mark_as_unclaimed']
    
    def original_purchase_details(self, obj):
        if obj.original_purchase:
            return format_html(
                '<strong>Voucher:</strong> {}<br>'
                '<strong>Purchased by:</strong> {}<br>'
                '<strong>Purchase Date:</strong> {}<br>'
                '<strong>Reference:</strong> {}',
                obj.original_purchase.voucher.title,
                obj.original_purchase.user.fullname,
                obj.original_purchase.purchased_at.strftime('%Y-%m-%d %H:%M'),
                obj.original_purchase.purchase_reference
            )
        return "No purchase details"
    original_purchase_details.short_description = 'Purchase Details'
    
    def mark_as_claimed(self, request, queryset):
        count = 0
        for gift_share in queryset:
            if not gift_share.is_claimed:
                gift_share.is_claimed = True
                gift_share.claimed_at = timezone.now()
                gift_share.save()
                count += 1
        self.message_user(request, f"Successfully marked {count} gift card shares as claimed.")
    mark_as_claimed.short_description = "Mark selected gift card shares as claimed"
    
    def mark_as_unclaimed(self, request, queryset):
        count = 0
        for gift_share in queryset:
            if gift_share.is_claimed:
                gift_share.is_claimed = False
                gift_share.claimed_at = None
                gift_share.claimed_by_user = None
                gift_share.save()
                count += 1
        self.message_user(request, f"Successfully marked {count} gift card shares as unclaimed.")
    mark_as_unclaimed.short_description = "Mark selected gift card shares as unclaimed"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'original_purchase', 'original_purchase__voucher', 'original_purchase__user', 'claimed_by_user'
        )
