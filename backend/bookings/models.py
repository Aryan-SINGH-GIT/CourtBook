from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Booking(models.Model):
    """Represents a court booking with associated resources"""
    
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='CONFIRMED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-start_time']
        
    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.start_time} to {self.end_time})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        from datetime import date
        
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time")
        
        if self.date < date.today():
            raise ValidationError("Cannot book for past dates")


class BookingResource(models.Model):
    """Tracks which resources are associated with a booking"""
    
    RESOURCE_TYPE_CHOICES = [
        ('COURT', 'Court'),
        ('EQUIPMENT', 'Equipment'),
        ('COACH', 'Coach'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='resources')
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPE_CHOICES)
    resource_id = models.PositiveIntegerField(help_text="ID of the resource (Court, Equipment, or Coach)")
    quantity = models.PositiveIntegerField(default=1, help_text="Quantity for equipment, 1 for court/coach")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['resource_type', 'resource_id']
        
    def __str__(self):
        return f"{self.booking} - {self.resource_type} #{self.resource_id}"
    
    def get_resource_object(self):
        """Helper method to get the actual resource object"""
        from resources.models import Court, Equipment, Coach
        
        resource_map = {
            'COURT': Court,
            'EQUIPMENT': Equipment,
            'COACH': Coach,
        }
        
        model_class = resource_map.get(self.resource_type)
        if model_class:
            try:
                return model_class.objects.get(id=self.resource_id)
            except model_class.DoesNotExist:
                return None
        return None
