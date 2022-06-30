from django.contrib import admin
from .models import OpayOrder, OrderResponse, PeriodOrderResponse, ATMCVSResponse,OpaySetting


# Register your models here.
class OpaySettingAdmin(admin.ModelAdmin):
    list_display = ('MerchantID',)
    exclude = ('PaymentType', 'EncryptType',)

class OpayOrderAdmin(admin.ModelAdmin):
    list_display = ('TotalAmount',)


class OrderResponseAdmin(admin.ModelAdmin):
    list_display = ('MerchantTradeNo',)


class PeriodOrderResponseAdmin(admin.ModelAdmin):
    list_display = ('MerchantTradeNo',)


class ATMCVSResponseAdmin(admin.ModelAdmin):
    list_display = ('MerchantTradeNo',)

admin.site.register(OpaySetting,OpaySettingAdmin)
admin.site.register(OpayOrder, OpayOrderAdmin)
admin.site.register(OrderResponse, OrderResponseAdmin)
admin.site.register(PeriodOrderResponse, PeriodOrderResponseAdmin)
admin.site.register(ATMCVSResponse, ATMCVSResponseAdmin)
