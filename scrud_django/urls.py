"""SCRUD DJANGO URL Configuration."""
from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from .rest import ResourceTypeViewSet, ResourceViewSet

router = routers.DefaultRouter()
router.register(r'resources', ResourceViewSet)
router.register(r'resource-types', ResourceTypeViewSet)

urlpatterns = [
    path('scrud/', include((router.urls, 'scrud'), namespace='scrud'))
]
