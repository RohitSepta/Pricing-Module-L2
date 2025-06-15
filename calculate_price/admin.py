from django.contrib import admin
from django.contrib import messages
from .models import PricingConfiguration, PricingConfigurationLog
from .forms import PricingConfigurationAdminForm

@admin.register(PricingConfiguration)
class PricingConfigurationAdmin(admin.ModelAdmin):
    form = PricingConfigurationAdminForm
    list_display = ['name', 'is_active', 'distance_base_price', 'base_distance_km', 'get_applicable_days_display', 'created_at', 'created_by']
    list_filter = ['is_active', 'created_at', 'applicable_days']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'created_by']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active', 'applicable_days')
        }),
        ('Distance Pricing', {
            'fields': ('distance_base_price', 'base_distance_km', 'distance_additional_price'),
            'description': 'Configure base price for initial distance and additional price per km'
        }),
        ('Time Multiplier', {
            'fields': ('time_multiplier_config',),
            'description': 'Configure time-based multipliers (JSON format)'
        }),
        ('Waiting Charges', {
            'fields': ('waiting_charge_per_interval', 'waiting_interval_minutes', 'waiting_free_minutes'),
            'description': 'Configure waiting charges'
        }),
        ('Metadata', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
            action = 'created'
        else:
            action = 'updated'
        
        super().save_model(request, obj, form, change)
        
        # Create log entry
        PricingConfigurationLog.objects.create(
            configuration=obj,
            action=action,
            actor=request.user,
            changes=form.changed_data if hasattr(form, 'changed_data') else []
        )
        
        messages.success(request, f'Pricing configuration "{obj.name}" has been {action} successfully.')
    
    def delete_model(self, request, obj):
        PricingConfigurationLog.objects.create(
            configuration=obj,
            action='deleted',
            actor=request.user,
            changes={}
        )
        super().delete_model(request, obj)

@admin.register(PricingConfigurationLog)
class PricingConfigurationLogAdmin(admin.ModelAdmin):
    list_display = ['configuration', 'action', 'actor', 'timestamp']
    list_filter = ['action', 'timestamp', 'actor']
    search_fields = ['configuration__name', 'actor__username']
    readonly_fields = ['configuration', 'action', 'actor', 'timestamp', 'changes']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False