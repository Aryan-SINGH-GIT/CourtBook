"""
Django Admin configuration for resources app
"""

from django.contrib import admin
from resources.models import Court, Equipment, Coach, CoachAvailability


class CoachAvailabilityInline(admin.TabularInline):
    """Inline admin for coach availability"""
    model = CoachAvailability
    extra = 1
    fields = ('date', 'start_time', 'end_time')


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    """Admin interface for Courts"""
    list_display = ('name', 'court_type', 'is_active', 'created_at')
    list_filter = ('court_type', 'is_active')
    search_fields = ('name',)
    list_editable = ('is_active',)
    ordering = ('name',)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    """Admin interface for Equipment"""
    list_display = ('name', 'total_quantity', 'available_quantity', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    """Admin interface for Coaches"""
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    list_editable = ('is_active',)
    inlines = [CoachAvailabilityInline]
    ordering = ('name',)


@admin.register(CoachAvailability)
class CoachAvailabilityAdmin(admin.ModelAdmin):
    """Admin interface for Coach Availability"""
    list_display = ('coach', 'date', 'start_time', 'end_time')
    list_filter = ('date', 'coach')
    search_fields = ('coach__name',)
    ordering = ('-date', 'start_time')
