from rest_framework import serializers
from rest_framework.reverse import reverse

from scrud_django import models


class ResourceSerializer(serializers.Serializer):
    class Meta:
        model = models.Resource
        fields = ['id', 'content', 'resource_type', 'modified_at', 'etag']

    def to_representation(self, instance):
        return instance.content


class ResourceEnvelopeSerializer(serializers.Serializer):
    class Meta:
        model = models.Resource
        fields = ['id', 'content', 'resource_type', 'modified_at', 'etag']
        content = ResourceSerializer()

    def to_representation(self, instance):
        return {
            'href': reverse(
                instance.resource_type.route_name_detail(), args=[instance.id]
            ),
            'last_modified': instance.modified_at.isoformat(),
            'etag': instance.etag,
            'content': self.Meta.content.to_representation(instance),
        }


class JSONSchemaSerializer(serializers.Serializer):
    """Serializer for JSON-Schema data."""

    class Meta:
        fields = ["$id", "$schema", "title", "description", "properties"]


class JSONLDSerializer(serializers.Serializer):
    """Serializer for JSON-LD data."""

    class Meta:
        fields = ["$id", "$schema", "title", "description", "properties"]
