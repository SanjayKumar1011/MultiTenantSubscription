from rest_framework import serializers
from django.contrib.auth import get_user_model
from organization.models import Organization

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'organization_name',
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_organization_name(self, value):
        if Organization.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Organization with this name already exists.")
        return value
    
    def create(self, validated_data):
        org_name = validated_data.pop('organization_name')

        organization = Organization.objects.create(name=org_name)

        user = User.objects.create_user(
            **validated_data,
            organization=organization,
            role='OWNER'
        )
        return user


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name')


class UserResponseSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'role',
            'organization',
        )

class InviteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'role')

    def validate_role(self, value):
        if value not in ['ADMIN', 'MEMBER']:
            raise serializers.ValidationError("Only ADMIN or MEMBER can be invited")
        return value

    def create(self, validated_data):
        request = self.context['request']
        inviter = request.user

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data['role'],
            organization=inviter.organization,
            invited_by=inviter
        )

        user.set_unusable_password()
        user.save()

        return user
