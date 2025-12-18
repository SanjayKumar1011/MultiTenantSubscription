from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Project
from .serializers import ProjectSerializer
from .permissions import ProjectPermission
from rest_framework.exceptions import PermissionDenied

class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, ProjectPermission]

    def get_queryset(self):
        # 🔐 Tenant-safe filtering
        return Project.objects.filter(
            organization=self.request.user.organization
        )

    def perform_create(self, serializer):
        # 🔐 Force tenant on creation
        organization = self.request.user.organization
        plan = organization.subscription.plan

        project_count = organization.projects.count()

        if project_count >= plan.max_projects:
            raise PermissionDenied(
            "Project limit reached. Upgrade your plan."
        )

        serializer.save(
        organization=organization,
        created_by=self.request.user
        )