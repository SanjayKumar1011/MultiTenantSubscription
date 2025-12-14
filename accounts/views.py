from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response    
from rest_framework.permissions import IsAuthenticated

# Create your views here.

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "organization": user.organization.name if user.organization else None,
        }
        return Response(data)