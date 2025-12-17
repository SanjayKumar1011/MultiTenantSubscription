from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Project
from .serializers import ProjectSerializer

class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 🔐 Tenant-safe filtering
        return Project.objects.filter(
            organization=self.request.user.organization
        )

    def perform_create(self, serializer):
        # 🔐 Force tenant on creation
        serializer.save(
            organization=self.request.user.organization
        )
