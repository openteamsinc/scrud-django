from rest_framework import serializers, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Resource, ResourceType

# Serializers define the API representation.


class ResourceTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ResourceType
        fields = ['type_uri', 'schema', 'context']


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Resource
        fields = ['content', 'resource_type', 'modified_at', 'etag']


# ViewSets define the view behavior.


class ResourceTypeViewSet(viewsets.ModelViewSet):
    queryset = ResourceType.objects.all()
    serializer_class = ResourceTypeSerializer
    permission_classes_mapping = {
        'list': [AllowAny],
        'create': [IsAuthenticated],
        'retrieve': [AllowAny],
        'update': [IsAuthenticated],
        'partial_update': [IsAuthenticated],
        'destroy': [IsAuthenticated],
    }


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes_mapping = {
        'list': [AllowAny],
        'create': [IsAuthenticated],
        'retrieve': [AllowAny],
        'update': [IsAuthenticated],
        'partial_update': [IsAuthenticated],
        'destroy': [IsAuthenticated],
    }
