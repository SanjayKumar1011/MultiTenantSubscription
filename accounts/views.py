from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response    
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializer import SignupSerializer,UserResponseSerializer, InviteUserSerializer
from .permissions import IsOwner, IsAdminOrOwner, IsMember
from django.contrib.auth import get_user_model  

User = get_user_model()

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

class UsersView(APIView):
    permission_classes = [IsOwner]

    def get(self, request):
        users = User.objects.filter(organization=request.user.organization)
        serializer = UserResponseSerializer(users, many=True)
        return Response(serializer.data)
    

class InviteUserAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrOwner]
    serializer_class = InviteUserSerializer
    def post(self, request):
        serializer = InviteUserSerializer(
            data=request.data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "User invited successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "invited_by": request.user.username,
                    "organization": user.organization.name if user.organization else None,
                }
            },
            status=status.HTTP_201_CREATED
        )
