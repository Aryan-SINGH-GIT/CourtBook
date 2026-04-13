"""
URL configuration for bookings app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from bookings.views import (
    BookingViewSet,
    CourtViewSet,
    EquipmentViewSet,
    CoachViewSet,
    DailyAvailabilityView,
    AddonAvailabilityView,
    AvailabilityView,
    PriceCalculationView,
    DashboardStatsView,
)

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'courts', CourtViewSet, basename='court')
router.register(r'equipment', EquipmentViewSet, basename='equipment')
router.register(r'coaches', CoachViewSet, basename='coach')

urlpatterns = [
    path('daily-matrix/', DailyAvailabilityView.as_view(), name='daily_matrix'),
    path('addon-availability/', AddonAvailabilityView.as_view(), name='addon_availability'),
    path('availability/', AvailabilityView.as_view(), name='availability'),
    path('price-calculation/', PriceCalculationView.as_view(), name='price_calculation'),
    path('admin/dashboard-stats/', DashboardStatsView.as_view(), name='admin_dashboard_stats'),
    path('', include(router.urls)),
]
