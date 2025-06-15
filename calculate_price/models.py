from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json

class PricingConfiguration(models.Model):
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Distance Base Price (DBP)
    distance_base_price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    base_distance_km = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    applicable_days = models.JSONField(default=list, help_text="List of days this config applies to")
    
    # Distance Additional Price (DAP)
    distance_additional_price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Time Multiplier Factor (TMF) - JSON field to store tiered multipliers
    time_multiplier_config = models.JSONField(
        default=dict,
        help_text="JSON config for time multipliers: {'1': 1.0, '2': 1.25, '3': 2.2}"
    )
    
    # Waiting Charges (WC)
    waiting_charge_per_interval = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    waiting_interval_minutes = models.IntegerField(default=3, validators=[MinValueValidator(1)])
    waiting_free_minutes = models.IntegerField(default=3, validators=[MinValueValidator(0)])
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"
    
    def get_applicable_days_display(self):
        return ", ".join(self.applicable_days)

class PricingConfigurationLog(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('activated', 'Activated'),
        ('deactivated', 'Deactivated'),
    ]
    
    configuration = models.ForeignKey(PricingConfiguration, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    actor = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(default=dict, help_text="Details of what changed")
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.configuration.name} - {self.action} by {self.actor.username} at {self.timestamp}"
