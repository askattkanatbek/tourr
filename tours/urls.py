from django.urls import path, include
from .views import MyToursListCreateView, MyTourDetailView, AllToursAdminsView, AdminUpdateTourView, TourCategoryViewSet, AdminAnalyticsView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'categories', TourCategoryViewSet, basename='tourcategory')
urlpatterns = [
    path('my-tours/', MyToursListCreateView.as_view(), name='my-tours',),
    path('my-tours/<int:pk>/', MyTourDetailView.as_view(), name='my-tour-detail'),
    path('all-tours/', AllToursAdminsView.as_view(), name='admin-all-tours'),
    path('all-tours/<int:pk>/', AdminUpdateTourView.as_view(), name='admin-tour-update'),
    path('', include(router.urls)),
    path('analytics/', AdminAnalyticsView.as_view(), name='admin-analytics')
]