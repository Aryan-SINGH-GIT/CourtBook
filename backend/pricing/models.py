from django.db import models
from django.core.validators import MinValueValidator


class PricingRule(models.Model):
    """Configuration-driven pricing rules for dynamic pricing"""
    
    RULE_TYPE_CHOICES = [
        ('PEAK_HOUR', 'Peak Hour Surcharge'),
        ('WEEKEND', 'Weekend Surcharge'),
        ('INDOOR_COURT', 'Indoor Court Premium'),
    ]
    
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES, unique=True)
    value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Percentage increase (e.g., 20 for 20%) or fixed amount"
    )
    is_percentage = models.BooleanField(
        default=True,
        help_text="If True, value represents a percentage. If False, a fixed amount."
    )
    description = models.CharField(max_length=255, blank=True, help_text="User-facing description of the rule")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['rule_type']
        
    def __str__(self):
        if self.is_percentage:
            return f"{self.get_rule_type_display()}: +{self.value}%"
        return f"{self.get_rule_type_display()}: +${self.value}"


class BasePrice(models.Model):
    """Base prices for various resources"""
    
    RESOURCE_TYPE_CHOICES = [
        ('COURT_HOUR', 'Court per Hour'),
        ('EQUIPMENT_HOUR', 'Equipment per Hour'),
        ('COACH_HOUR', 'Coach per Hour'),
    ]
    
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES, unique=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['resource_type']
        verbose_name_plural = 'Base Prices'
        
    def __str__(self):
        return f"{self.get_resource_type_display()}: ${self.price}"
