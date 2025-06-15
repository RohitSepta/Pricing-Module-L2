from rest_framework import serializers
from .models import PricingConfiguration, PricingConfigurationLog

class PricingConfigurationSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    applicable_days_display = serializers.CharField(source='get_applicable_days_display', read_only=True)
    
    class Meta:
        model = PricingConfiguration
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by']

class PricingConfigurationLogSerializer(serializers.ModelSerializer):
    actor = serializers.StringRelatedField(read_only=True)
    configuration = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = PricingConfigurationLog
        fields = '__all__'

class PricingCalculationSerializer(serializers.Serializer):
    distance_km = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=0)
    total_time_hours = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=0)
    waiting_time_minutes = serializers.IntegerField(min_value=0)
    day_of_week = serializers.ChoiceField(choices=[
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ])