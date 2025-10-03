from django.contrib import admin

from .models import PhoneNumber


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('area_code', 'local_number', 'cost')
    search_fields = ('area_code', 'local_number')
    list_filter = ('area_code',)
