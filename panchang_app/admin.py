from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import CustomUser, Panchang, Festival, ShubhaMuhurt, KundaliRecord, LocationMaster

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'name', 'phone_number', 'is_staff', 'is_active']
    search_fields = ['email', 'name']
    ordering = ['email']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone_number', 'password'),
        }),
    )

@admin.register(Panchang)
class PanchangAdmin(admin.ModelAdmin):
    list_display = ['date', 'tithi', 'vaar', 'nakshatra', 'sunrise', 'sunset']
    list_filter = ['is_ekadashi', 'is_pournima', 'is_amavasya', 'is_sankashti']
    search_fields = ['tithi', 'vaar', 'nakshatra']
    ordering = ['date']

@admin.register(Festival)
class FestivalAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'category']
    list_filter = ['category', 'date']
    search_fields = ['name', 'description']
    ordering = ['date']

@admin.register(ShubhaMuhurt)
class ShubhaMuhurtAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'start_time', 'end_time']
    list_filter = ['category', 'start_time']
    search_fields = ['name', 'description']
    ordering = ['start_time']

SHANTI_PUJAN_CHOICES = [
    ('नवग्रह शांती', 'नवग्रह शांती'),
    ('गुरु शांती', 'गुरु शांती'),
    ('मंगळ दोष शांती', 'मंगळ दोष शांती'),
    ('शनि शांती', 'शनि शांती'),
    ('राहु-केतु शांती', 'राहु-केतु शांती'),
    ('कालसर्प दोष', 'कालसर्प दोष'),
    ('पितृ दोष शांती', 'पितृ दोष शांती'),
    ('त्रीपिंडी श्राद्ध', 'त्रीपिंडी श्राद्ध'),
    ('चांडाळ योग शांती', 'चांडाळ योग शांती'),
    ('नक्षत्र शांती', 'नक्षत्र शांती'),
    ('लक्ष्मी शांती', 'लक्ष्मी शांती'),
    ('महामृत्युंजय जप', 'महामृत्युंजय जप'),
    ('वास्तु शांती', 'वास्तु शांती'),
    ('कुंभ विवाह', 'कुंभ विवाह'),
    ('नवचंडी विधान', 'नवचंडी विधान'),
]

MANTRA_UPASANA_CHOICES = [
    ('सूर्य', 'सूर्य'),
    ('चन्द्र', 'चन्द्र'),
    ('मंगळ', 'मंगळ'),
    ('बुध', 'बुध'),
    ('गुरु', 'गुरु'),
    ('शुक्र', 'शुक्र'),
    ('शनि', 'शनि'),
    ('राहू', 'राहू'),
    ('केतु', 'केतु'),
    ('महा मृत्युंजय मंत्र', 'महा मृत्युंजय मंत्र'),
]

class KundaliRecordAdminForm(forms.ModelForm):
    shanti_pujan = forms.MultipleChoiceField(
        choices=SHANTI_PUJAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="आवश्यक शांती पूजन"
    )
    mantra_upasana = forms.MultipleChoiceField(
        choices=MANTRA_UPASANA_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="मंत्र उपासना"
    )

    class Meta:
        model = KundaliRecord
        fields = '__all__'

@admin.register(KundaliRecord)
class KundaliRecordAdmin(admin.ModelAdmin):
    form = KundaliRecordAdminForm
    list_display = ['name', 'user', 'gender', 'date_of_birth', 'time_of_birth', 'place_of_birth', 'latitude', 'longitude', 'timezone']
    list_filter = ['gender', 'date_of_birth']
    search_fields = ['name', 'place_of_birth', 'user__email']
    ordering = ['-created_at']

    class Media:
        js = (
            'https://cdn.tiny.cloud/1/no-api-key/tinymce/6/tinymce.min.js',
            'js/admin_rich_text.js',
        )

import csv
import json
import io
from django.urls import path
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse

@admin.register(LocationMaster)
class LocationMasterAdmin(admin.ModelAdmin):
    list_display = ['location_name', 'district', 'state', 'country', 'latitude', 'longitude', 'timezone', 'is_active']
    list_filter = ['state', 'country', 'is_active']
    search_fields = ['location_name', 'district', 'state']
    ordering = ['location_name']
    actions = ['soft_delete_locations', 'restore_locations', 'export_locations_csv', 'export_locations_json']

    @admin.action(description='Soft delete selected locations')
    def soft_delete_locations(self, request, queryset):
        rows_updated = queryset.update(is_active=False)
        self.message_user(request, f"{rows_updated} location(s) successfully soft-deleted.")

    @admin.action(description='Restore selected soft-deleted locations')
    def restore_locations(self, request, queryset):
        rows_updated = queryset.update(is_active=True)
        self.message_user(request, f"{rows_updated} location(s) successfully restored.")

    @admin.action(description='Export selected locations as CSV')
    def export_locations_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="locations.csv"'
        writer = csv.writer(response)
        writer.writerow(['location_name', 'country', 'state', 'district', 'city_village', 'latitude', 'longitude', 'timezone', 'is_active'])
        for loc in queryset:
            writer.writerow([loc.location_name, loc.country, loc.state, loc.district, loc.city_village, loc.latitude, loc.longitude, loc.timezone, loc.is_active])
        return response

    @admin.action(description='Export selected locations as JSON')
    def export_locations_json(self, request, queryset):
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="locations.json"'
        data = []
        for loc in queryset:
            data.append({
                'location_name': loc.location_name,
                'country': loc.country,
                'state': loc.state,
                'district': loc.district,
                'city_village': loc.city_village,
                'latitude': str(loc.latitude),
                'longitude': str(loc.longitude),
                'timezone': loc.timezone,
                'is_active': loc.is_active
            })
        response.write(json.dumps(data, indent=2))
        return response

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-locations/', self.admin_site.admin_view(self.import_locations_view), name='import_locations'),
        ]
        return custom_urls + urls

    def import_locations_view(self, request):
        if request.method == 'POST' and request.FILES.get('import_file'):
            import_file = request.FILES['import_file']
            file_name = import_file.name
            try:
                count = 0
                if file_name.endswith('.csv'):
                    decoded_file = import_file.read().decode('utf-8')
                    io_string = io.StringIO(decoded_file)
                    reader = csv.reader(io_string)
                    header = next(reader)
                    for row in reader:
                        if len(row) >= 8:
                            loc_name = row[0]
                            country = row[1]
                            state = row[2]
                            district = row[3]
                            city_village = row[4]
                            lat = float(row[5])
                            lon = float(row[6])
                            tz = row[7]
                            is_active = row[8].lower() == 'true' if len(row) > 8 else True
                            
                            LocationMaster.objects.update_or_create(
                                location_name=loc_name,
                                latitude=lat,
                                longitude=lon,
                                defaults={
                                    'country': country,
                                    'state': state,
                                    'district': district,
                                    'city_village': city_village,
                                    'timezone': tz,
                                    'is_active': is_active
                                }
                            )
                            count += 1
                elif file_name.endswith('.json'):
                    decoded_file = import_file.read().decode('utf-8')
                    data = json.loads(decoded_file)
                    for item in data:
                        LocationMaster.objects.update_or_create(
                            location_name=item.get('location_name'),
                            latitude=float(item.get('latitude')),
                            longitude=float(item.get('longitude')),
                            defaults={
                                'country': item.get('country', 'India'),
                                'state': item.get('state', ''),
                                'district': item.get('district', ''),
                                'city_village': item.get('city_village', ''),
                                'timezone': item.get('timezone', 'Asia/Kolkata'),
                                'is_active': item.get('is_active', True)
                            }
                        )
                        count += 1
                self.message_user(request, f"Successfully imported {count} location(s).")
                return HttpResponseRedirect("../")
            except Exception as e:
                self.message_user(request, f"Error importing locations: {e}", level=messages.ERROR)
                return HttpResponseRedirect("../")
                
        from django.template.response import TemplateResponse
        context = {
            **self.admin_site.each_context(request),
            'title': 'Import Locations (CSV or JSON)',
            'opts': self.model._meta,
        }
        return TemplateResponse(request, "admin/import_locations.html", context)

admin.site.register(CustomUser, CustomUserAdmin)
