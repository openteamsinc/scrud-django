"""SCRUD DJANGO URL Configuration."""
from django.urls import path

from scrud_django.views import (
    ResourceCollectionContextView,
    ResourceCollectionSchemaView,
)

urlpatterns = [
    path(
        "collections-json-schema/<str:slug>/",
        ResourceCollectionSchemaView.as_view(),
        name="collections-json-schema",
    ),
    path(
        "collections-json-ld/<str:slug>/",
        ResourceCollectionContextView.as_view(),
        name="collections-json-ld",
    ),
]
