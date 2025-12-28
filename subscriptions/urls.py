from django.urls import path,include
from .views import UpgradeSubscriptionAPIView

urlpatterns = [
    # Define your subscription-related URL patterns here    
    path('subscriptions/upgrade',UpgradeSubscriptionAPIView.as_view(),name='change_plan'),
]