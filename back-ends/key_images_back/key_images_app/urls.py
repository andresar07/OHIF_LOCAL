from django.urls import path
from key_images_app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('health', views.health, name='health'),
    path('store', views.store, name='store'),
    path('retrieve', views.retrieve, name='retrieve'),
    path('delete/<str:key>', views.delete, name='delete')
]