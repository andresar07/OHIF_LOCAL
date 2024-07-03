"""
key_images_back URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
from django.urls import path, include
from django.conf import settings

from drf_yasg import openapi
from drf_yasg.views import get_schema_view as swagger_get_schema_view

schema_view = swagger_get_schema_view(
    openapi.Info(
        title="Key Images Backend",
        default_version="1.0.0",
        description="API documentation of Key Images Back-end @ IMEXHS",
    ),
    public=False,
)

urlpatterns = [
    path('viewer/keyimages/', include('key_images_app.urls')),
]

# swagger endpoints documentation only on debug
if settings.DEBUG:
    urlpatterns.append(path('viewer/keyimages/swagger/docs', schema_view.with_ui('swagger', cache_timeout=0), name="swagger_schema"))
