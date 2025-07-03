from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

# DRF JWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# DRF YASG (если используешь его)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# DRF SPECTACULAR
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

schema_view = get_schema_view(
    openapi.Info(
        title="Telegram Login API",
        default_version='v1',
        description="API для входа и подтверждения через Telegram",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Основное API
    path('api/', include('users.urls')),

    # Swagger (drf-yasg)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # Spectacular schema + Swagger (альтернатива)
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger-alt/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui-alt'),


    path('api/tours/', include('tours.urls')),  # чтобы не пересекалось
]
