from django.urls import path
from .views import SignupView, MeView

urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('me/', MeView.as_view()),
]
