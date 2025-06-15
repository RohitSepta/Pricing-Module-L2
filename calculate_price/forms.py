from django import forms
from django.core.exceptions import ValidationError
from .models import PricingConfiguration
import json

class PricingConfigurationAdminForm(forms.ModelForm):
    DAYS_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    applicable_days = forms.MultipleChoiceField(
        choices=DAYS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Select the days this pricing configuration applies to"
    )
    
    time_multiplier_config = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        help_text='Enter time multipliers in JSON format: {"1": 1.0, "2": 1.25, "3": 2.2} (hour: multiplier)',
        initial='{"1": 1.0, "2": 1.25, "3": 2.2}'
    )
    
    class Meta:
        model = PricingConfiguration
        exclude = ['created_by']
    
    def clean_time_multiplier_config(self):
        data = self.cleaned_data['time_multiplier_config']
        try:
            parsed_data = json.loads(data)
            if not isinstance(parsed_data, dict):
                raise ValidationError("Time multiplier config must be a JSON object")
            
            for hour, multiplier in parsed_data.items():
                try:
                    int(hour)
                    float(multiplier)
                except (ValueError, TypeError):
                    raise ValidationError(f"Invalid hour '{hour}' or multiplier '{multiplier}'. Hours must be integers and multipliers must be numbers.")
                
                if float(multiplier) <= 0:
                    raise ValidationError("Multipliers must be positive numbers")
            
            return parsed_data
        except json.JSONDecodeError:
            raise ValidationError("Invalid JSON format for time multiplier config")
    
    def clean_distance_base_price(self):
        price = self.cleaned_data['distance_base_price']
        if price <= 0:
            raise ValidationError("Distance base price must be positive")
        return price
    
    def clean_base_distance_km(self):
        distance = self.cleaned_data['base_distance_km']
        if distance <= 0:
            raise ValidationError("Base distance must be positive")
        return distance
    
    def clean_distance_additional_price(self):
        price = self.cleaned_data['distance_additional_price']
        if price < 0:
            raise ValidationError("Distance additional price cannot be negative")
        return price

class PricingCalculationForm(forms.Form):
    distance_km = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        help_text="Total distance traveled in kilometers"
    )
    
    total_time_hours = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        help_text="Total trip time in hours"
    )
    
    waiting_time_minutes = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Total waiting time in minutes"
    )
    
    day_of_week = forms.ChoiceField(
        choices=[
            ('monday', 'Monday'),
            ('tuesday', 'Tuesday'),
            ('wednesday', 'Wednesday'),
            ('thursday', 'Thursday'),
            ('friday', 'Friday'),
            ('saturday', 'Saturday'),
            ('sunday', 'Sunday'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Day of the week for the trip"
    )