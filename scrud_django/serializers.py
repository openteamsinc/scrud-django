from rest_framework import serializers

from scrud_django import models


class ResourceSerializer(serializers.Serializer):
    class Meta:
        model = models.Resource
        fields = ['id', 'content', 'resource_type', 'modified_at', 'etag']

    def to_representation(self, instance):
        # result = super().to_representation(instance)
        return {
            'id': instance.id,
            'content': instance.content,
            'resource_type': instance.resource_type.type_uri,
            'modified_at': instance.modified_at.isoformat(),
            'etag': instance.etag,
        }


class JSONSchemaSerializer(serializers.Serializer):
    """Serializer for JSON-Schema data."""

    class Meta:
        fields = ["$id", "$schema", "title", "description", "properties"]


class JSONLDSerializer(serializers.Serializer):
    """Serializer for JSON-LD data."""

    class Meta:
        fields = ["$id", "$schema", "title", "description", "properties"]
