from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from decimal import Decimal
import json
import math

from .models import PricingConfiguration, PricingConfigurationLog
from .forms import PricingCalculationForm
from .serializers import PricingConfigurationSerializer, PricingCalculationSerializer

class PricingConfigurationViewSet(viewsets.ModelViewSet):
    queryset = PricingConfiguration.objects.all()
    serializer_class = PricingConfigurationSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

def pricing_calculator_view(request):
    result = None
    config_used = None
    
    if request.method == 'POST':
        form = PricingCalculationForm(request.POST)
        if form.is_valid():
            try:
                result, config_used = calculate_pricing(
                    distance_km=form.cleaned_data['distance_km'],
                    total_time_hours=form.cleaned_data['total_time_hours'],
                    waiting_time_minutes=form.cleaned_data['waiting_time_minutes'],
                    day_of_week=form.cleaned_data['day_of_week']
                )
                messages.success(request, f'Price calculated successfully using configuration: {config_used.name}')
            except Exception as e:
                messages.error(request, f'Error calculating price: {str(e)}')
    else:
        form = PricingCalculationForm()
    
    active_configs = PricingConfiguration.objects.filter(is_active=True)
    
    return render(request, 'calculator.html', {
        'form': form,
        'result': result,
        'config_used': config_used,
        'active_configs': active_configs,
    })

@api_view(['POST'])
def calculate_price_api(request):
    serializer = PricingCalculationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            result, config_used = calculate_pricing(
                distance_km=serializer.validated_data['distance_km'],
                total_time_hours=serializer.validated_data['total_time_hours'],
                waiting_time_minutes=serializer.validated_data['waiting_time_minutes'],
                day_of_week=serializer.validated_data['day_of_week']
            )
            
            return Response({
                'total_price': result['total_price'],
                'breakdown': result['breakdown'],
                'configuration_used': {
                    'id': config_used.id,
                    'name': config_used.name,
                    'description': config_used.description
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def calculate_pricing(distance_km, total_time_hours, waiting_time_minutes, day_of_week):
    """
    Calculate pricing using the formula: Price = (DBP + (Dn * DAP)) * TMF + WC
    """
    # Find active configuration for the given day
    config = PricingConfiguration.objects.filter(
        is_active=True,
        applicable_days__icontains=day_of_week
    ).first()
    if not config:
        raise ValueError(f"No active pricing configuration found for {day_of_week}")
    
    # Distance Base Price (DBP)
    dbp = config.distance_base_price
    
    # Calculate additional distance
    additional_distance = max(0, distance_km - config.base_distance_km)
    
    # Distance Additional Price (DAP)
    dap = additional_distance * config.distance_additional_price
    
    # Base distance + additional distance cost
    distance_cost = dbp + dap
    
    # Time Multiplier Factor (TMF)
    time_multiplier = calculate_time_multiplier(total_time_hours, config.time_multiplier_config)
    
    # Apply time multiplier to distance cost
    time_adjusted_cost = distance_cost * Decimal(str(time_multiplier))
    
    # Waiting Charges (WC)
    waiting_charges = calculate_waiting_charges(
        waiting_time_minutes,
        config.waiting_free_minutes,
        config.waiting_charge_per_interval,
        config.waiting_interval_minutes
    )
    
    # Final price calculation
    total_price = time_adjusted_cost + waiting_charges
    
    # Breakdown for transparency
    breakdown = {
        'distance_base_price': float(dbp),
        'base_distance_km': float(config.base_distance_km),
        'additional_distance_km': float(additional_distance),
        'distance_additional_cost': float(dap),
        'total_distance_cost': float(distance_cost),
        'time_multiplier': float(time_multiplier),
        'time_adjusted_cost': float(time_adjusted_cost),
        'waiting_charges': float(waiting_charges),
        'total_price': float(total_price)
    }
    
    return {
        'total_price': float(total_price),
        'breakdown': breakdown
    }, config

def calculate_time_multiplier(total_time_hours, time_multiplier_config):
    """Calculate time multiplier based on tiered structure"""
    time_hours = float(total_time_hours)
    
    # Sort hours in ascending order
    sorted_hours = sorted([int(h) for h in time_multiplier_config.keys()])
    
    # Find applicable tier
    multiplier = 1.0
    for hour_threshold in sorted_hours:
        if time_hours >= hour_threshold:
            multiplier = float(time_multiplier_config[str(hour_threshold)])
        else:
            break
    
    return multiplier

def calculate_waiting_charges(waiting_time_minutes, free_minutes, charge_per_interval, interval_minutes):
    """Calculate waiting charges based on intervals"""
    if waiting_time_minutes <= free_minutes:
        return Decimal('0')
    
    chargeable_minutes = waiting_time_minutes - free_minutes
    intervals = math.ceil(chargeable_minutes / interval_minutes)
    
    return intervals * charge_per_interval