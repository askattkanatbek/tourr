from rest_framework import generics, permissions, viewsets
from .models import Tour, TourCategory
from users.permissions import IsAdminUser
from .serializers import TourSerializer, TourCategorySerializer
from .permissions import IsTourCreater
from .analytics import get_admin_analytics
from rest_framework.views import APIView
from rest_framework.response import Response

class MyToursListCreateView(generics.ListCreateAPIView):
    serializer_class = TourSerializer
    permission_classes = [IsTourCreater]

    def get_queryset(self):
        return Tour.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class MyTourDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TourSerializer
    permission_classes = [IsTourCreater]

    def get_queryset(self):
        return Tour.objects.filter(created_by=self.request.user)


class AllToursAdminsView(generics.ListAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = [IsAdminUser]


class AdminUpdateTourView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = [IsAdminUser]


class TourCategoryViewSet(viewsets.ModelViewSet):
    queryset = TourCategory.objects.all()
    serializer_class = TourCategorySerializer
    permission_classes = [IsAdminUser]


class AdminAnalyticsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = get_admin_analytics()
        return Response(data)