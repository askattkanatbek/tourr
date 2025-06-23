from django.contrib import admin
from .models import Tour, TourCategory


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'status', 'price', 'start_date', 'end_date')
    list_filter = ('status', 'start_date')
    search_fields = ('title', 'description')

admin.site.register(TourCategory)