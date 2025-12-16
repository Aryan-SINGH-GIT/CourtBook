"""
REST API Views and ViewSets for the booking system
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from datetime import datetime, time, timedelta
from bookings.daily_availability_serializers import CourtDailyAvailabilitySerializer

from bookings.models import Booking, BookingResource
from bookings.serializers import (
    BookingListSerializer,
    BookingCreateSerializer,
    AvailabilityQuerySerializer,
    AvailabilityResponseSerializer,
    PriceCalculationSerializer,
    CourtSerializer,
    EquipmentSerializer,
    CoachSerializer,
)
from bookings.services.booking_service import BookingService
from resources.services.availability_service import AvailabilityService
from pricing.services.pricing_service import PricingService
from resources.models import Court, Equipment, Coach


class AvailabilityView(APIView):
    """Check availability of courts, coaches, and equipment for a time slot"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=AvailabilityQuerySerializer,
        responses={200: AvailabilityResponseSerializer},
        description="Query available resources for a given date and time range",
        tags=['Booking'],
        examples=[
            OpenApiExample(
                'Example Request',
                value={
                    "date": "2025-12-16",
                    "start_time": "10:00",
                    "end_time": "11:00"
                },
                request_only=True,
            ),
        ]
    )
    def post(self, request):
        """
        POST /api/availability/
        Query available resources for a given date/time
        """
        serializer = AvailabilityQuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        booking_date = data['date']
        start_time = data['start_time']
        end_time = data['end_time']
        
        # Get available resources
        available_courts = AvailabilityService.get_available_courts(
            booking_date, start_time, end_time
        )
        available_coaches = AvailabilityService.get_available_coaches(
            booking_date, start_time, end_time
        )
        equipment_availability = AvailabilityService.get_equipment_availability(
            booking_date, start_time, end_time
        )
        
        # Serialize equipment availability
        equipment_data = [
            {
                'id': item['equipment'].id,
                'name': item['equipment'].name,
                'available_quantity': item['available_quantity'],
                'total_quantity': item['total_quantity']
            }
            for item in equipment_availability
        ]
        
        response_data = {
            'courts': CourtSerializer(available_courts, many=True).data,
            'coaches': CoachSerializer(available_coaches, many=True).data,
            'equipment': equipment_data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class PriceCalculationView(APIView):
    """Calculate price for a booking before creating it"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=PriceCalculationSerializer,
        description="Calculate total price for selected resources with pricing rules applied",
        tags=['Booking'],
        examples=[
            OpenApiExample(
                'Example Request',
                value={
                    "date": "2025-12-16",
                    "start_time": "10:00",
                    "end_time": "11:00",
                    "court_id": 1,
                    "equipment": [{"id": 1, "quantity": 2}],
                    "coach_id": 1
                },
                request_only=True,
            ),
        ]
    )
    def post(self, request):
        """
        POST /api/price-calculation/
        Calculate total price for selected resources
        """
        serializer = PriceCalculationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Prepare equipment list
        equipment_list = None
        if data.get('equipment'):
            equipment_list = [
                {'id': eq['id'], 'quantity': eq['quantity']}
                for eq in data['equipment']
            ]
        
        try:
            price_breakdown = PricingService.calculate_booking_price(
                booking_date=data['date'],
                start_time=data['start_time'],
                end_time=data['end_time'],
                court_id=data['court_id'],
                equipment_list=equipment_list,
                coach_id=data.get('coach_id')
            )
            return Response(price_breakdown, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing bookings"""
    permission_classes = [IsAuthenticated]
    serializer_class = BookingListSerializer
    
    def get_queryset(self):
        """Return bookings for the current user, or all if staff"""
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all().select_related('user').prefetch_related('resources')
        return Booking.objects.filter(user=user).select_related('user').prefetch_related('resources')
    
    @extend_schema(
        request=BookingCreateSerializer,
        responses={201: BookingListSerializer},
        description="Create a new booking with atomic transaction handling",
        tags=['Booking'],
        examples=[
            OpenApiExample(
                'Example Request',
                value={
                    "date": "2025-12-16",
                    "start_time": "10:00",
                    "end_time": "11:00",
                    "court_id": 1,
                    "equipment": [{"id": 1, "quantity": 2}],
                    "coach_id": 1
                },
                request_only=True,
            ),
        ]
    )
    def create(self, request):
        """
        POST /api/bookings/
        Create a new booking atomically
        """
        serializer = BookingCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Prepare equipment list
        equipment_list = None
        if data.get('equipment'):
            equipment_list = [
                {'id': eq['id'], 'quantity': eq['quantity']}
                for eq in data['equipment']
            ]
        
        try:
            result = BookingService.create_booking(
                user=request.user,
                booking_date=data['date'],
                start_time=data['start_time'],
                end_time=data['end_time'],
                court_id=data['court_id'],
                equipment_list=equipment_list,
                coach_id=data.get('coach_id')
            )
            
            # Return the created booking
            booking_serializer = BookingListSerializer(result['booking'])
            response_data = {
                **booking_serializer.data,
                'price_breakdown': result['price_breakdown'],
                'message': result['message']
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        POST /api/bookings/{id}/cancel/
        Cancel a booking
        """
        try:
            result = BookingService.cancel_booking(
                booking_id=pk,
                user=request.user
            )
            return Response(result, status=status.HTTP_200_OK)
            
        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        GET /api/bookings/history/
        Get user's booking history
        """
        bookings = BookingService.get_user_bookings(request.user)
        serializer = BookingListSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourtViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing courts (read-only)"""
    permission_classes = [IsAuthenticated]
    queryset = Court.objects.filter(is_active=True)
    serializer_class = CourtSerializer


class EquipmentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing equipment (read-only)"""
    permission_classes = [IsAuthenticated]
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer


class CoachViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing coaches (read-only)"""
    permission_classes = [AllowAny]  # Public access for landing page
    queryset = Coach.objects.filter(is_active=True)
    serializer_class = CoachSerializer

from bookings.daily_availability_serializers import DailyAvailabilityQuerySerializer, CourtDailyAvailabilitySerializer
from datetime import datetime, timedelta, time

class DailyAvailabilityView(APIView):
    """
    Get availability matrix for all courts on a specific date.
    Used for the grid-based booking UI.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='date', description='Date to check (YYYY-MM-DD)', required=True, type=OpenApiTypes.DATE),
        ],
        responses={200: CourtDailyAvailabilitySerializer(many=True)},
        description="Get daily checking availability for all courts",
        tags=['Booking']
    )
    def get(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': 'Date parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

        # Get all active courts
        courts = Court.objects.filter(is_active=True).order_by('id')
        
        # Get all bookings for the date in one go
        bookings = Booking.objects.filter(
            date=query_date,
            status='CONFIRMED',  
            resources__resource_type='COURT'
        ).prefetch_related('resources')

        # Define time slots (06:00 to 22:00)
        start_hour = 6
        end_hour = 22
        slots_def = [time(hour=h, minute=0) for h in range(start_hour, end_hour + 1)]

        # Optimization: Map bookings by court_id for O(1) lookup
        # Structure: { court_id: [booking_obj, booking_obj, ...] }
        bookings_by_court = {court.id: [] for court in courts}
        
        for booking in bookings:
            for resource in booking.resources.all():
                if resource.resource_type == 'COURT' and resource.resource_id in bookings_by_court:
                    bookings_by_court[resource.resource_id].append(booking)

        result = []
        user_id = request.user.id
        
        # Get base court price
        court_base_price = PricingService.get_base_price('COURT_HOUR')
        
        for court in courts:
            court_bookings = bookings_by_court.get(court.id, [])
            court_slots = []
            
            for slot_time in slots_def:
                # Find if any booking covers this slot
                # A booking covers a slot if booking_start <= slot_time < booking_end
                slot_booking = None
                
                # Since court_bookings is small (max ~16 per day), linear scan is fine here
                for booking in court_bookings:
                    if booking.start_time <= slot_time and booking.end_time > slot_time:
                        slot_booking = booking
                        break
                
                # Calculate price for this specific slot
                # Assuming 1 hour slots for the matrix
                slot_end_dt = datetime.combine(query_date, slot_time) + timedelta(hours=1)
                slot_end_time = slot_end_dt.time()
                
                final_price, _ = PricingService.apply_pricing_rules(
                    court_base_price,
                    query_date,
                    slot_time,
                    slot_end_time,
                    court.id
                )
                
                court_slots.append({
                    'time': slot_time,
                    'is_booked': slot_booking is not None,
                    'booking_id': slot_booking.id if slot_booking else None,
                    'is_user_booking': slot_booking.user_id == user_id if slot_booking else False,
                    'price': final_price
                })
        
            result.append({
                'id': court.id,
                'name': court.name,
                'slots': court_slots
            })
            
        return Response(result, status=status.HTTP_200_OK)


class AddonAvailabilityView(APIView):
    """
    Get availability for Equipment and Coaches for a specific time slot.
    Used in Step 2 of the booking flow.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='date', type=OpenApiTypes.DATE, required=True),
            OpenApiParameter(name='start_time', type=OpenApiTypes.TIME, required=True),
            OpenApiParameter(name='end_time', type=OpenApiTypes.TIME, required=True),
        ],
        description="Get available addons (equipment/coaches) for a specific slot",
        tags=['Booking']
    )
    def get(self, request):
        try:
            date_str = request.query_params.get('date')
            start_str = request.query_params.get('start_time')
            end_str = request.query_params.get('end_time')

            if not all([date_str, start_str, end_str]):
                return Response({'error': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)

            booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Parse time strings (handle HH:MM:SS or HH:MM)
            def parse_time(t_str):
                try:
                    return datetime.strptime(t_str, '%H:%M:%S').time()
                except ValueError:
                    return datetime.strptime(t_str, '%H:%M').time()
            
            start_time = parse_time(start_str)
            end_time = parse_time(end_str)

            # Get Coach Availability
            available_coaches = AvailabilityService.get_available_coaches(
                booking_date, start_time, end_time
            )

            # Get Equipment Availability
            equipment_availability = AvailabilityService.get_equipment_availability(
                booking_date, start_time, end_time
            )
            
            # Serialize
            equipment_data = [
                {
                    'id': item['equipment'].id,
                    'name': item['equipment'].name,
                    'available_quantity': item['available_quantity'],
                    'total_quantity': item['total_quantity'],
                    # Basic price estimation could be added here if needed
                }
                for item in equipment_availability
            ]

            return Response({
                'coaches': CoachSerializer(available_coaches, many=True).data,
                'equipment': equipment_data
            })

        except ValueError:
            return Response({'error': 'Invalid date/time format'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
