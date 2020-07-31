from typing import Optional

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from scrud_django import serializers
from scrud_django.models import Resource, ResourceType
from scrud_django.paginations import StandardResultsSetPagination
from scrud_django.registration import ResourceRegistration

# RESOURCE


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = serializers.ResourceSerializer
    pagination_class = StandardResultsSetPagination

    # scrud variable
    resource_type_name: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resource_type_name = kwargs.get('resource_type_name')

    def get_permissions(self):
        """
        Returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def create(self, request):
        """Create a Resource."""
        instance = ResourceRegistration.register(
            content=request.data, register_type=self.resource_type_name
        )
        serializer = self.serializer_class(instance=instance, many=False)
        return Response(serializer.data)

    def update(self, request, slug: str):
        """Update a Resource."""
        instance = ResourceRegistration.update(
            content=request.data,
            register_type=self.resource_type_name,
            slug=slug,
        )
        serializer = self.serializer_class(instance=instance, many=False)
        return Response(serializer.data)

    def destroy(self, request, slug: str):
        """Update a Resource."""
        ResourceRegistration.delete(
            register_type=self.resource_type_name, slug=slug,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, slug: str):
        """Return the resource for the given resource type name."""
        resource_type = get_object_or_404(
            ResourceType, slug=self.resource_type_name
        )
        instance = get_object_or_404(
            Resource, resource_type=resource_type, pk=int(slug)
        )

        serializer = self.serializer_class(instance=instance, many=False)
        return Response(serializer.data)

    def list(self, request):
        """Return the resource for the given resource type name."""
        resource_type = get_object_or_404(
            ResourceType, slug=self.resource_type_name
        )

        instance = Resource.objects.filter(resource_type=resource_type)
        serializer = self.serializer_class(instance=instance, many=True)
        page = self.get_paginated_response(serializer.data)

        return Response(page)


# JSON-SCHEMA


class JSONSchemaViewSet(viewsets.ViewSet):
    """View set for JSON-Schema requests."""

    serializer_class = serializers.JSONSchemaSerializer
    permission_classes_mapping = {
        'list': [AllowAny],
        'create': [IsAuthenticated],
        'retrieve': [AllowAny],
        'update': [IsAuthenticated],
        'partial_update': [IsAuthenticated],
        'destroy': [IsAuthenticated],
    }

    def get_queryset(self):
        return ResourceType.objects.all()

    def create(self, request, data: dict):
        """Return the JSON Schema for the given Resource."""
        raise NotImplementedError('``Create`` not implemented yet.')

    def retrieve(self, request, slug: str):
        """Return the JSON Schema for the given Resource."""
        resource_type = ResourceType.objects.filter(type_uri=slug)
        instance = Resource.objects.filter(resource_type=resource_type)
        serializer = self.serializer_class(instance=instance, many=False)
        return Response(serializer.data)

    def list(self, request):
        """Return the JSON Schema for the given Resource."""
        instance = Resource.objects.filter()
        serializer = self.serializer_class(instance=instance, many=True)
        return Response(serializer.data)


# JSON-SCHEMA


class JSONLDViewSet(viewsets.ViewSet):
    """View set for JSON-LD requests."""

    serializer_class = serializers.JSONLDSerializer
    permission_classes_mapping = {
        'list': [AllowAny],
        'create': [IsAuthenticated],
        'retrieve': [AllowAny],
        'update': [IsAuthenticated],
        'partial_update': [IsAuthenticated],
        'destroy': [IsAuthenticated],
    }

    def get_queryset(self):
        return ResourceType.objects.all()

    def create(self, request, data: dict):
        """Return the JSON LD for the given Resource."""
        raise NotImplementedError('``Create`` not implemented yet.')

    def retrieve(self, request, slug: str):
        """Return the JSON LD for the given Resource."""
        resource_type = ResourceType.objects.filter(type_uri=slug)
        instance = Resource.objects.filter(resource_type=resource_type)
        serializer = self.serializer_class(instance=instance, many=False)
        return Response(serializer.data)

    def list(self, request):
        """Return the JSON LD for the given Resource."""
        instance = Resource.objects.filter()
        serializer = self.serializer_class(instance=instance, many=True)
        return Response(serializer.data)
