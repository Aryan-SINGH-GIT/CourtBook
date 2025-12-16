"""
Django Admin configuration for bookings app
"""

from django.contrib import admin
from bookings.models import Booking, BookingResource


class BookingResourceInline(admin.TabularInline):
    """Inline admin for booking resources"""
    model = BookingResource
    extra = 0
    can_delete = False
    readonly_fields = ('resource_type', 'resource_id', 'quantity', 'created_at')
    fields = ('resource_type', 'resource_id', 'quantity')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin interface for Bookings (mostly read-only)"""
    list_display = ('id', 'user', 'date', 'start_time', 'end_time', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('user', 'date', 'start_time', 'end_time', 'total_price', 'created_at', 'updated_at')
    inlines = [BookingResourceInline]
    ordering = ('-date', '-start_time')
    list_per_page = 50
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'date', 'start_time', 'end_time')
        }),
        ('Pricing', {
            'fields': ('total_price',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['cancel_bookings']
    
    def cancel_bookings(self, request, queryset):
        """Bulk action to cancel bookings"""
        confirmed_bookings = queryset.filter(status='CONFIRMED')
        count = confirmed_bookings.update(status='CANCELLED')
        self.message_user(request, f'{count} booking(s) successfully cancelled.')
    
    cancel_bookings.short_description = "Cancel selected bookings"


@admin.register(BookingResource)
class BookingResourceAdmin(admin.ModelAdmin):
    """Admin interface for Booking Resources"""
    list_display = ('booking', 'resource_type', 'resource_id', 'quantity', 'created_at')
    list_filter = ('resource_type', 'created_at')
    search_fields = ('booking__user__username',)
    readonly_fields = ('booking', 'resource_type', 'resource_id', 'quantity', 'created_at')
    ordering = ('-created_at',)
