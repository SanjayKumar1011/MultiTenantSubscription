from rest_framework import serializers
from subscriptions.models import Plan

class UpgradeSubscriptionSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()

    def validate_plan_id(self, value):
        try:
            plan = Plan.objects.get(id=value)
        except Plan.DoesNotExist:
            raise serializers.ValidationError("Invalid plan")

        return plan
