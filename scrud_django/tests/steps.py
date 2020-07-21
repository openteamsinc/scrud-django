from datetime import datetime

from django.db.models import Model
from safetydance import step_data
from safetydance_test.step_extension import step_extension

from ..models import Resource, ResourceType

named_instances = step_data(dict, initializer=dict)


@step_extension
def an_instance_named(name: str, instance: Model):
    named_instances[name] = instance


@step_extension
def is_valid_resource(name: str):
    instance = named_instances[name]
    assert isinstance(instance, Resource)
    assert isinstance(instance.content, dict)
    assert isinstance(instance.modified_at, datetime)
    assert isinstance(instance.etag, str)
    assert len(instance.etag) == 32


@step_extension
def is_valid_resource_type(name: str):
    instance = named_instances[name]
    assert isinstance(instance, ResourceType)
    assert isinstance(instance.type_uri, str)
    assert len(instance.type_uri) > 0
