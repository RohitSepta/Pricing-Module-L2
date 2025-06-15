from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'pricing-configs', views.PricingConfigurationViewSet)

urlpatterns = [
    path('', views.pricing_calculator_view, name='pricing_calculator'),
    path('api/', include(router.urls)),
    path('api/calculate-price/', views.calculate_price_api, name='calculate_price_api'),
]