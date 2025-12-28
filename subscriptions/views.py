from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from subscriptions.models import Subscription
from .serializers import UpgradeSubscriptionSerializer
from accounts.permissions import IsOwner

class UpgradeSubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def post(self, request):
        serializer = UpgradeSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plan = serializer.validated_data['plan_id']

        subscription, created = Subscription.objects.get_or_create(
            organization=request.user.organization,
            defaults={
                'plan': plan,
                'status': 'ACTIVE'
            }
        )

        if not created:
            subscription.plan = plan
            subscription.status = 'ACTIVE'
            subscription.save()

        return Response({
            "message": "Subscription upgraded successfully",
            "plan": plan.name
        })
