from django.urls import path
from .views import SignupView, MeView, InviteUserAPIView

urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('me/', MeView.as_view()),
    path('invite/', InviteUserAPIView.as_view()),
]
