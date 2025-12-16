from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response    
from rest_framework.permissions import IsAuthenticated
from .serializer import SignupSerializer,UserResponseSerializer
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


class SignupView(APIView):

    permission_classes = []
    serializer_class = SignupSerializer
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.save()
            response_data = UserResponseSerializer(user).data
            return Response({"message": "Signup successful","user": response_data
                             }, status=201)
        return Response(serializer.errors, status=400)
