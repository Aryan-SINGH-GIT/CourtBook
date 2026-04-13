from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import models
from django.db.models import Avg
from .models import Review
from resources.models import Court, Coach

@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_rating(sender, instance, **kwargs):
    booking = instance.booking
    
    # Check if booking has resources (Court or Coach)
    # A booking can have multiple resources, we should rate the PRIMARY resource or all?
    # Based on models, BookingResource links Booking to resources.
    # The review is for the 'Booking' which might contain a Court and a Coach.
    # For simplicity, we will update the Court and Coach present in the booking.
    
    resources = booking.resources.all()
    
    for resource_link in resources:
        resource = resource_link.get_resource_object()
        
        if isinstance(resource, (Court, Coach)):
            # Find all bookings for this resource that have a review
            # We need to query Reviews where review.booking.resources contains this resource
            
            # This complex query is expensive. 
            # Alternative: Just query all reviews for bookings that have this resource.
            # But Review -> Booking -> BookingResource -> Resource(ID+Type)
            
            # Filter all BookingResources that match this resource linked to Completed bookings with reviews
            from bookings.models import BookingResource
            
            # Find all booking IDs that used this resource
            booking_ids = BookingResource.objects.filter(
                resource_type=resource_link.resource_type,
                resource_id=resource_link.resource_id
            ).values_list('booking_id', flat=True)
            
            # Find all reviews for these bookings
            reviews = Review.objects.filter(booking_id__in=booking_ids)
            
            # specific aggregation
            aggregates = reviews.aggregate(Avg('rating'), count=models.Count('id'))
            
            avg_rating = aggregates['rating__avg'] or 0
            count = aggregates['count']
            
            # Update the resource
            resource.average_rating = round(avg_rating, 1)
            resource.rating_count = count
            resource.save()

from django.db import models
