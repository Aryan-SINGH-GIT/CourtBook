from django.urls import path
from .views import PublicPricingView

urlpatterns = [
    path('config/', PublicPricingView.as_view(), name='pricing-config'),
]
