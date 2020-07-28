"""
This will support queries, such as:
    GET /resource_type/schema?uri=http://schema.org/person
    GET /resource_type/context?uri=http://schema.org/person

"""
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext_lazy as _


class ResourceType(models.Model):
    type_uri = models.URLField()
    schema = models.ForeignKey(
        'Resource',
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_('schema resource type'),
        related_name='resource_type_schema',
    )
    context = models.ForeignKey(
        'Resource',
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_('context resource type'),
        related_name='resource_type_context',
    )


class Resource(models.Model):
    # The actual JSON content for this resource
    content = JSONField()
    resource_type = models.ForeignKey(
        ResourceType,
        on_delete=models.PROTECT,
        verbose_name=_('resource type'),
        related_name='resource_type',
    )
    modified_at = models.DateTimeField()
    etag = models.CharField(max_length=40)
