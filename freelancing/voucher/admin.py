from django.contrib import admin

# Register your models here.

from freelancing.voucher.models import Voucher, VoucherType , UserVoucherRedemption

admin.site.register(Voucher)
admin.site.register(VoucherType)
admin.site.register(UserVoucherRedemption)