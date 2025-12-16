from django.db import models


class Court(models.Model):
    """Represents a badminton court"""
    
    COURT_TYPE_CHOICES = [
        ('INDOOR', 'Indoor'),
        ('OUTDOOR', 'Outdoor'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    court_type = models.CharField(max_length=10, choices=COURT_TYPE_CHOICES, default='INDOOR')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.get_court_type_display()})"


class Equipment(models.Model):
    """Represents equipment available for rental (rackets, shuttlecocks, etc.)"""
    
    name = models.CharField(max_length=100)
    total_quantity = models.PositiveIntegerField(default=0)
    available_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Equipment'
        
    def __str__(self):
        return f"{self.name} ({self.available_quantity}/{self.total_quantity} available)"
    
    def save(self, *args, **kwargs):
        # Ensure available_quantity doesn't exceed total_quantity
        if self.available_quantity > self.total_quantity:
            self.available_quantity = self.total_quantity
        super().save(*args, **kwargs)


class Coach(models.Model):
    """Represents a coach available for booking"""
    
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Coaches'
        
    def __str__(self):
        return self.name


class CoachAvailability(models.Model):
    """Tracks when coaches are available for booking"""
    
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date', 'start_time']
        verbose_name_plural = 'Coach Availabilities'
        unique_together = ['coach', 'date', 'start_time']
        
    def __str__(self):
        return f"{self.coach.name} - {self.date} ({self.start_time} to {self.end_time})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Ensure times are present before comparing
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time")
