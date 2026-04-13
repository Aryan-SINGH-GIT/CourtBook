from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from bookings.models import Booking
from django.contrib.auth.models import User

class DashboardStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = timezone.now().date()
        last_30_days = today - timedelta(days=30)

        # Total Revenue (All time)
        total_revenue = Booking.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
        
        # Monthly Revenue
        monthly_revenue = Booking.objects.filter(
            created_at__gte=last_30_days
        ).aggregate(Sum('total_price'))['total_price__sum'] or 0

        # Total Bookings
        total_bookings = Booking.objects.count()

        # Active Users (Users who have made at least one booking)
        active_users = User.objects.annotate(
            booking_count=Count('bookings')
        ).filter(booking_count__gt=0).count()

        # Recent Bookings (Last 5)
        recent_bookings = Booking.objects.select_related('user').order_by('-created_at')[:5].values(
            'id', 'user__username', 'date', 'start_time', 'total_price', 'status'
        )

        return Response({
            'total_revenue': total_revenue,
            'monthly_revenue': monthly_revenue,
            'total_bookings': total_bookings,
            'active_users': active_users,
            'recent_bookings': list(recent_bookings)
        })
