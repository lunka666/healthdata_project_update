from django.contrib import admin
from .models import HealthRecord

@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ('patient_full_name', 'measurement_date', 'blood_type', 'heart_rate')
    search_fields = ('patient_full_name', 'blood_type')
    list_filter = ('blood_type', 'measurement_date')
