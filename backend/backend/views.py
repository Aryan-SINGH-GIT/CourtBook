"""
API Root view to show available endpoints
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    API Root - Badminton Court Booking System
    Returns available API endpoints
    """
    return Response({
        'message': 'Welcome to Badminton Court Booking System API',
        'version': '1.0',
        'documentation': {
            'swagger_ui': request.build_absolute_uri('/api/docs/'),
            'redoc': request.build_absolute_uri('/api/redoc/'),
            'openapi_schema': request.build_absolute_uri('/api/schema/'),
        },
        'endpoints': {
            'authentication': {
                'register': reverse('auth_register', request=request, format=format),
                'login': reverse('token_obtain_pair', request=request, format=format),
                'refresh': reverse('token_refresh', request=request, format=format),
            },
            'resources': {
                'courts': request.build_absolute_uri('/api/courts/'),
                'equipment': request.build_absolute_uri('/api/equipment/'),
                'coaches': request.build_absolute_uri('/api/coaches/'),
            },
            'booking': {
                'availability': reverse('availability', request=request, format=format),
                'price_calculation': reverse('price_calculation', request=request, format=format),
                'bookings': request.build_absolute_uri('/api/bookings/'),
                'booking_history': request.build_absolute_uri('/api/bookings/history/'),
            },
            'admin': {
                'admin_dashboard': request.build_absolute_uri('/admin/'),
            }
        },
        'quick_start': {
            'note': 'Most API endpoints require JWT authentication',
            'auth_header': 'Authorization: Bearer <access_token>',
            'explore_api': 'Visit Swagger UI for interactive API documentation',
        }
    })
