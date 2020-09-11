import logging
from datetime import datetime
from uuid import uuid4

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import path

from scrud_django.models import Resource, ResourceType


class ResourceTypeRegistration:
    def __init__(
        self,
        resource_type_uri: str,
        schema_resource: Resource = None,
        schema_uri: str = None,
        context_resource: Resource = None,
        context_uri: str = None,
        slug: str = None,
    ):
        """
        Register resource type model.
        """
        search = ResourceType.objects.filter(type_uri=resource_type_uri)
        if search:
            self.resource_type = search[0]
        else:
            resource_type = ResourceType(
                type_uri=resource_type_uri,
                schema=schema_resource,
                schema_uri=schema_uri,
                context=context_resource,
                context_uri=context_uri,
                slug=slug,
                etag=uuid4().hex,
                modified_at=datetime.now(),
            )
            resource_type.save()
            self.resource_type = resource_type
        self.register_urls()

    def register_urls(self):
        """Register resource type url."""
        from scrud_django import views

        scrud_list = views.ResourceViewSet.as_view(
            {'get': 'list', 'post': 'create'},
            resource_type_name=self.resource_type.slug,
        )
        scrud_detail = views.ResourceViewSet.as_view(
            {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'},
            resource_type_name=self.resource_type.slug,
        )
        self.urls = [
            path(
                f'{self.resource_type.slug}/',
                scrud_list,
                # name=f'{resource_type.slug}-list',
                name=self.resource_type.route_name_list(),
            ),
            path(
                f'{self.resource_type.slug}/<str:slug>/',
                scrud_detail,
                # name=f'{resource_type.slug}-detail',
                name=self.resource_type.route_name_detail(),
            ),
        ]


class ResourceRegistration:
    @staticmethod
    def register(content: str, register_type: str) -> Resource:
        """
        Register resource content for the given resource type name.

        Parameters
        ----------
        content : dict
        register_type : str

        Returns
        -------
        Resource

        """
        with transaction.atomic():
            resource_type = get_object_or_404(ResourceType, slug=register_type)

            resource = Resource(
                content=content,
                resource_type=resource_type,
                etag=uuid4().hex,
                modified_at=datetime.now(),
            )
            resource_type.etag = resource.etag
            resource_type.modified_at = resource.modified_at
            resource.save()
            resource_type.save()
        return resource

    @staticmethod
    def update(content: str, register_type: str, slug: str) -> Resource:
        """
        Update resource content for the given resource type name and slug.

        Parameters
        ----------
        content : dict
        register_type : str
        slug : str

        Returns
        -------
        Resource

        """
        with transaction.atomic():
            resource_type = get_object_or_404(ResourceType, slug=register_type)

            # note: for now slug is used as ID
            resource = get_object_or_404(
                Resource, resource_type=resource_type, pk=int(slug)
            )

            resource.content = content
            resource.etag = uuid4().hex
            resource.modified_at = datetime.now()
            resource_type.etag = resource.etag
            resource_type.modified_at = resource.modified_at
            resource.save()
            resource_type.save()
        return resource

    @staticmethod
    def delete(register_type: str, slug: str):
        """
        Delete resource for the given resource type name and slug.

        Parameters
        ----------
        register_type : str
        slug : str

        """
        with transaction.atomic():
            resource_type = get_object_or_404(ResourceType, slug=register_type)

            # note: for now slug is used as ID
            resource = get_object_or_404(
                Resource, resource_type=resource_type, pk=int(slug)
            )
            resource.delete()
            resource_type.etag = uuid4().hex
            resource_type.modified_at = datetime.now()
            resource_type.save()


JSON_SCHEMA_REGISTRATION_ = None
JSON_SCHEMA_RESOURCE_TYPE_ = None
JSON_LD_RESOURCE_TYPE_ = None
JSON_LD_REGISTRATION_ = None


def register_json_schema_resource_type():
    global JSON_SCHEMA_RESOURCE_TYPE_
    global JSON_SCHEMA_REGISTRATION_
    if JSON_SCHEMA_RESOURCE_TYPE_ is None:
        JSON_SCHEMA_REGISTRATION_ = ResourceTypeRegistration(
            resource_type_uri="http://json-schema.org/draft-04/schema",
            schema_uri="http://json-schema.org/draft-04/schema",
            slug="json-schema",
        )
        JSON_SCHEMA_RESOURCE_TYPE_ = JSON_SCHEMA_REGISTRATION_.resource_type
    return JSON_SCHEMA_RESOURCE_TYPE_


def register_json_ld_resource_type():
    global JSON_LD_RESOURCE_TYPE_
    global JSON_LD_REGISTRATION_
    if JSON_LD_RESOURCE_TYPE_ is None:
        JSON_LD_REGISTRATION_ = ResourceTypeRegistration(
            resource_type_uri="http://www.w3.org/ns/json-ld#context",
            slug="json-ld",
        )
        JSON_LD_RESOURCE_TYPE_ = JSON_LD_REGISTRATION_.resource_type
    return JSON_LD_RESOURCE_TYPE_


def register_file(file_to_register, resource_type):
    resource = None
    try:
        contents = file_to_register.read()
        resource = ResourceRegistration.register(contents, resource_type.slug)
    except Exception as e:
        logging.error(e)
    finally:
        file_to_register.close()
    return resource


def register_json_schema(schema_file):
    resource_type = register_json_schema_resource_type()
    return register_file(schema_file, resource_type)


def register_json_ld_context(context_file):
    resource_type = register_json_ld_resource_type()
    return register_file(context_file, resource_type)


def json_resource_type(
    resource_type_uri: str,
    schema_resource: Resource = None,
    schema_file=None,
    schema_uri: str = None,
    context_resource: Resource = None,
    context_file=None,
    context_uri: str = None,
):
    """Registration of a single json resource type. Callers **should** provide one and
    only one of `schema_resource, schema_file, schema_uri` as well as one and only  one
    of `context_resource, context_file, context_uri`.
    """
    if schema_resource is None and schema_file is not None:
        schema_resource = register_json_schema(schema_file)
    if context_resource is None and context_file is not None:
        context_resource = register_json_ld_context(context_file)
    resource_type_registration = ResourceTypeRegistration(
        resource_type_uri,
        schema_resource=schema_resource,
        schema_uri=schema_uri,
        context_resource=context_resource,
        context_uri=context_uri,
    )
    return resource_type_registration.urls


def json_resource_types(configuration_dict):
    """Registration of multiple resource types.
    resource_type_uri -> configuration
    """
    urls = []
    for resource_type_uri, configuration in configuration_dict.items():
        urls.extend(json_resource_type(resource_type_uri, **configuration))
    return urls
