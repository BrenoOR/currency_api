from django.contrib import admin
from .models import Rate, Checker


class RateAdmin(admin.ModelAdmin):
    list_display = ('base_currency', 'target_currency', 'rate', 'timestamp',)
    list_filter = ('base_currency', 'target_currency',)


class CheckerAdmin(admin.ModelAdmin):
    list_display = ('base_currency', 'target_currency', 'check_period',)
    list_filter = ('base_currency', 'target_currency',)


admin.site.register(Rate, RateAdmin)
admin.site.register(Checker, CheckerAdmin)
