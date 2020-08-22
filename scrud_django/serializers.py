from django.db.models import Manager
from rest_framework import serializers
from rest_framework.reverse import reverse_lazy

from scrud_django import models


class EnvelopeSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        iterable = data.all() if isinstance(data, Manager) else data
        return [
            self.child.to_representation(item, envelope=True)
            for item in iterable
        ]


class ResourceSerializer(serializers.Serializer):
    class Meta:
        model = models.Resource
        list_serializer_class = EnvelopeSerializer

    def to_representation(self, instance, envelope=False, context=None):
        if not envelope:
            return instance.content
        request = self._context["request"]
        return {
            'href': reverse_lazy(
                instance.resource_type.route_name_detail(),
                args=[instance.id],
                request=request,
            ),
            'last_modified': instance.modified_at.isoformat(),
            'etag': instance.etag,
            'content': instance.content,
        }


class JSONSchemaSerializer(serializers.Serializer):
    """Serializer for JSON-Schema data."""

    class Meta:
        fields = ["$id", "$schema", "title", "description", "properties"]


class JSONLDSerializer(serializers.Serializer):
    """Serializer for JSON-LD data."""

    class Meta:
        fields = ["$id", "$schema", "title", "description", "properties"]
