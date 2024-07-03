from django.urls import path
from django.conf import settings

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from . import views

app_name = 'Annotations_app'

schema_view = get_schema_view(
   openapi.Info(
      title="API documentation for module annotation back-end",
      default_version='v1',
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', views.index, name='Index message'),
    path('health', views.health, name='Health message'),
    path('post-new-annotation/<str:study_id>', views.save_new_annotation, name='Set new annotations'),
    path('get-study-annotations/<str:study_id>', views.get_study_annotations, name='Get study annotations'),
]

if settings.TESTING:
    urlpatterns.append(path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'))
    urlpatterns.append(path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'))