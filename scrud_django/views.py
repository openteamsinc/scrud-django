from datetime import timezone
from functools import wraps
from typing import Optional

from django.shortcuts import get_object_or_404
from django.utils.cache import get_conditional_response
from django.utils.http import http_date, quote_etag
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy

from scrud_django import serializers
from scrud_django.models import Resource, ResourceType
from scrud_django.paginations import StandardResultsSetPagination
from scrud_django.registration import ResourceRegistration


def link_content(url, rel, content_type):
    return f"<{url}>; rel=\"{rel}\"; type=\"{content_type}\""


def get_string_or_evaluate(string_or_func, view_set, request, *args, **kwargs):
    if not string_or_func:
        return None
    if isinstance(string_or_func, str):
        return string_or_func
    return string_or_func(view_set, request, *args, **kwargs)


def scrudful(
    etag_func=None,
    last_modified_func=None,
    schema_link_or_func=None,
    context_link_or_func=None,
    http_schema_or_func=None,
):
    """Decorator to make a view method SCRUDful"""
    # TODO what about 400 Bad Request context and schema?
    def decorator(view_method):
        @wraps(view_method)
        def inner(self, request, *args, **kwargs):
            if request.method in ("PUT", "DELETE"):
                missing_required_headers = []
                if etag_func and not request.META.get("HTTP_IF_MATCH"):
                    missing_required_headers.append("If-Match")
                if last_modified_func and not request.META.get(
                    "HTTP_IF_UNMODIFIED_SINCE"
                ):
                    missing_required_headers.append("If-Unmodified-Since")
                if missing_required_headers:
                    # TODO Define standard error json
                    response = Response(
                        {"missing-required-headers": missing_required_headers},
                        status=400,
                    )
                    return response

            # Compute values (if any) for the requested resource.
            def get_last_modified():
                if last_modified_func:
                    last_modified = last_modified_func(
                        self, request, *args, **kwargs
                    )
                    if last_modified:
                        return http_date(
                            last_modified.replace(
                                tzinfo=timezone.utc
                            ).timestamp()
                        )
                return None

            if request.method not in ("POST", "OPTIONS"):
                print(args)
                print(kwargs)
                etag = (
                    etag_func(self, request, *args, **kwargs)
                    if etag_func
                    else None
                )
                etag = quote_etag(etag) if etag else None
                last_modified = get_last_modified()
            else:
                etag = None
                last_modified = None
            response = get_conditional_response(
                request, etag=etag, last_modified=last_modified
            )
            if response is None:
                response = view_method(self, request, *args, **kwargs)
                schema_link = (
                    get_string_or_evaluate(
                        schema_link_or_func, self, request, *args, **kwargs
                    )
                    or ""
                )
                context_link = (
                    get_string_or_evaluate(
                        context_link_or_func, self, request, *args, **kwargs
                    )
                    or ""
                )
                join_links = ", " if schema_link and context_link else ""
                link_content = schema_link + join_links + context_link
                if etag:
                    response["ETag"] = etag
                if last_modified:
                    response["Last-Modified"] = last_modified
                if link_content:
                    response["Link"] = link_content
            return response

        setattr(inner, "http_schema_or_func", http_schema_or_func)
        return inner

    return decorator


def scrudful_viewset(cls):
    meta = getattr(cls, "Meta", None)
    etag_func = getattr(meta, "etag_func", None)
    last_modified_func = getattr(meta, "last_modified_func", None)
    schema_link_or_func = getattr(meta, "schema_link_or_func", None)
    context_link_or_func = getattr(meta, "context_link_or_func", None)
    scrudful_item = scrudful(
        etag_func=etag_func,
        last_modified_func=last_modified_func,
        schema_link_or_func=schema_link_or_func,
        context_link_or_func=context_link_or_func,
    )
    for method_name in ("create", "retrieve", "update", "destroy"):
        method = getattr(cls, method_name)
        setattr(cls, method_name, scrudful_item(method))
    if hasattr(cls, "list"):
        scrudful_list = scrudful(
            etag_func=getattr(meta, "list_etag_func", None),
            last_modified_func=getattr(meta, "list_last_modified_func", None),
            schema_link_or_func=getattr(
                meta, "list_schema_link_or_func", None
            ),
            context_link_or_func=getattr(
                meta, "list_context_link_or_func", None
            ),
        )
        list_method = getattr(cls, "list")
        setattr(cls, "list", scrudful_list(list_method))
    return cls


# RESOURCE


@scrudful_viewset
class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = serializers.ResourceSerializer
    pagination_class = StandardResultsSetPagination

    # scrud variable
    resource_type_name: Optional[str] = None

    class Meta:
        def etag_func(view_instance, request, slug: str):
            instance = view_instance.get_instance(request, slug)
            return instance.etag

        def last_modified_func(view_instance, request, slug: str):
            instance = view_instance.get_instance(request, slug)
            return instance.modified_at

        def schema_link_or_func(view_instance, request, slug: str = None):
            if view_instance.resource_type_name:
                resource_type = get_object_or_404(
                    ResourceType, slug=view_instance.resource_type_name
                )
                if resource_type.schema_uri:
                    uri = resource_type.schema_uri
                elif resource_type.schema:
                    schema = resource_type.schema
                    uri = reverse_lazy(
                        schema.resource_type.route_name_detail(),
                        args=[schema.id],
                        request=request,
                    )
                if uri:
                    return link_content(uri, "describedBy", "application/json")
            return None

        def context_link_or_func(view_instance, request, slug: str = None):
            if view_instance.resource_type_name:
                resource_type = get_object_or_404(
                    ResourceType, slug=view_instance.resource_type_name
                )
                if resource_type.context_uri:
                    uri = resource_type.context_uri
                elif resource_type.context:
                    context = resource_type.context
                    uri = reverse_lazy(
                        context.resource_type.route_name_detail(),
                        args=[context.id],
                        request=request,
                    )
                if uri:
                    return link_content(
                        uri,
                        "http://www.w3.org/ns/json-ld#context",
                        "application/ld+json",
                    )

        def list_etag_func(request, *args, **kwargs):
            return "YYYY"

        # list_last_modified_func =
        list_schema_link_or_func = "list-schema-tbd"
        list_context_link_or_func = "list-context-tbd"

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

    def get_instance(self, request, slug: str):
        resource_type = get_object_or_404(
            ResourceType, slug=self.resource_type_name
        )
        instance = get_object_or_404(
            Resource, resource_type=resource_type, pk=int(slug)
        )
        return instance

    def create(self, request):
        """Create a Resource."""
        instance = ResourceRegistration.register(
            content=request.data, register_type=self.resource_type_name
        )
        serializer = self.get_serializer(instance=instance, many=False)
        return Response(serializer.data)

    def update(self, request, slug: str):
        """Update a Resource."""
        instance = ResourceRegistration.update(
            content=request.data,
            register_type=self.resource_type_name,
            slug=slug,
        )
        serializer = self.get_serializer(instance=instance, many=False)
        return Response(serializer.data)

    def destroy(self, request, slug: str):
        """Update a Resource."""
        ResourceRegistration.delete(
            register_type=self.resource_type_name, slug=slug,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, slug: str):
        """Return the resource for the given resource type name."""
        instance = self.get_instance(request, slug)
        serializer = self.get_serializer(instance=instance, many=False)
        return Response(serializer.data)

    def list(self, request):
        """Return the resource for the given resource type name."""
        resource_type = get_object_or_404(
            ResourceType, slug=self.resource_type_name
        )

        queryset = Resource.objects.filter(resource_type=resource_type)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(self.get_paginated_response(serializer.data))

        serializer = self.get_serializer(instance=queryset, many=True)
        return Response(serializer.data)


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
