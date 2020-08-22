from datetime import datetime
from typing import Dict, List
from uuid import uuid4

import yaml
from django.shortcuts import get_object_or_404
from django.urls import path

from scrud_django.models import Resource, ResourceType


class ResourceTypeRegistration:
    data_source: Dict = {}
    resource_type_list: List[ResourceType] = []
    urls: List[str] = []

    def __init__(self, yaml_path):
        with open(yaml_path) as f:
            self.data_source = yaml.load(f, Loader=yaml.FullLoader)

        # force a creation of a new list
        self.resource_type_list = []

        for k, v in self.data_source.items():
            self.register_model(
                json_schema_url=v['json_schema_url'],
                json_ld_context_url=v['json_ld_context_url'],
                rdf_type_uri=v['rdf_type_uri'],
                slug=k,
            )
        self.register_urls()

    def register_model(
        self,
        json_schema_url: str,
        json_ld_context_url: str,
        rdf_type_uri: str,
        slug: str,
    ):
        """
        Register resource type model.

        Parameters
        ----------
        json_schema_url : str
        json_ld_context_url : str
        rdf_type_uri : str
        slug : str

        """
        data = dict(
            schema_uri=json_schema_url,
            context_uri=json_ld_context_url,
            type_uri=rdf_type_uri,
            slug=slug,
        )

        search = ResourceType.objects.filter(**data)
        if search:
            self.resource_type_list.append(search[0])
            return

        rt = ResourceType(**data)
        rt.save()
        self.resource_type_list.append(rt)

    def register_urls(self):
        """Register resource type url."""
        from scrud_django import views

        # json-schema
        json_schema_list = views.JSONSchemaViewSet.as_view(
            {'get': 'list', 'post': 'create'}
        )
        json_schema_detail = views.JSONSchemaViewSet.as_view(
            {'get': 'retrieve'}
        )

        # json-ld
        json_ld_list = views.JSONLDViewSet.as_view(
            {'get': 'list', 'post': 'create'}
        )
        json_ld_detail = views.JSONLDViewSet.as_view({'get': 'retrieve'})

        urls = [
            path('json-schema/', json_schema_list, name='json-schema-list'),
            path(
                'json-schema/<str:slug>/',
                json_schema_detail,
                name='json-schema-detail',
            ),
            # JSON LD
            path('json-ld/', json_ld_list, name='json-ld-list'),
            path(
                'json-ld/<str:slug>/', json_ld_detail, name='json-ld-detail',
            ),
        ]

        for resource_type in self.resource_type_list:
            # scrud
            scrud_list = views.ResourceViewSet.as_view(
                {'get': 'list', 'post': 'create'},
                resource_type_name=resource_type.slug,
            )
            scrud_detail = views.ResourceViewSet.as_view(
                {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'},
                resource_type_name=resource_type.slug,
            )

            # JSON SCHEMA

            # SCRUD, note: it should be at the end of the list
            # note: it maybe
            urls.append(
                path(
                    f'{resource_type.slug}/',
                    scrud_list,
                    # name=f'{resource_type.slug}-list',
                    name=resource_type.route_name_list(),
                ),
            )
            urls.append(
                path(
                    f'{resource_type.slug}/<str:slug>/',
                    scrud_detail,
                    # name=f'{resource_type.slug}-detail',
                    name=resource_type.route_name_detail(),
                )
            )
        self.urls = urls


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
        resource_type = get_object_or_404(ResourceType, slug=register_type)

        resource = Resource(
            content=content,
            resource_type=resource_type,
            etag=uuid4().hex,
            modified_at=datetime.now(),
        )
        resource.save()
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
        resource_type = get_object_or_404(ResourceType, slug=register_type)

        # note: for now slug is used as ID
        resource = get_object_or_404(
            Resource, resource_type=resource_type, pk=int(slug)
        )

        resource.content = content
        resource.etag = uuid4().hex
        resource.modified_at = datetime.now()

        resource.save()
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
        resource_type = get_object_or_404(ResourceType, slug=register_type)

        # note: for now slug is used as ID
        resource = get_object_or_404(
            Resource, resource_type=resource_type, pk=int(slug)
        )
        resource.delete()
