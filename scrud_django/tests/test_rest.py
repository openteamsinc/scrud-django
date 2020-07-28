import json
import os

import pytest
from django.urls import reverse
from rest_framework import status
from safetydance_django.test import http  # noqa: F401
from safetydance_test import Given, Then, scripted_test

from .factories import ResourceFactory, ResourceTypeFactory, UserFactory

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT_PATH, 'data')


@pytest.fixture
def regular_login():
    return UserFactory()


@pytest.fixture
def admin_login():
    return UserFactory(is_staff=True)


# RESOURCE

RESOURCE_ENDPOINT_PREFIX = "scrud:resource"
RESOURCE_ENDPOINT_DETAIL_NAME = f"{RESOURCE_ENDPOINT_PREFIX}-detail"
RESOURCE_ENDPOINT_LIST_NAME = f"{RESOURCE_ENDPOINT_PREFIX}-list"


@pytest.fixture
def new_resource_data():
    resource_type = ResourceTypeFactory(
        type_uri='https://schema.org/givenName'
    )
    return {
        'content': {'name': 'Gandhi'},
        # it should be changed to a url
        'resource_type': resource_type.id,
    }


@pytest.mark.django_db
@scripted_test
def test_resource_get_list(regular_login):
    Given.http.get(reverse(RESOURCE_ENDPOINT_LIST_NAME))
    Then.http.status_code_is(status.HTTP_200_OK)


@pytest.mark.skip(
    'skipping now for "django.core.exceptions.ImproperlyConfigured" error'
)
@pytest.mark.django_db
@scripted_test
def test_resource_get_detail(regular_login):
    # generate a data for searching
    data = ResourceFactory()
    Given.http.get(
        reverse(RESOURCE_ENDPOINT_DETAIL_NAME, kwargs={'pk': data.id})
    )
    Then.http.status_code_is(status.HTTP_200_OK)


@pytest.mark.skip('skipping now for permission issues')
@pytest.mark.django_db
@scripted_test
def test_resource_post(new_resource_data):
    Given.http.post(
        reverse(RESOURCE_ENDPOINT_LIST_NAME),
        json.dump(new_resource_data),
        content_type='application/json',
    )
    Then.http.status_code_is(status.HTTP_200_OK)


@pytest.mark.skip('skipping now for permission issues')
@pytest.mark.django_db
@scripted_test
def test_resource_put(new_resource_data):
    data_factory = ResourceFactory()

    Given.http.post(
        reverse(RESOURCE_ENDPOINT_LIST_NAME, kwargs={'pk': data_factory.id}),
        json.dump(new_resource_data),
        content_type='application/json',
    )
    Then.http.status_code_is(status.HTTP_200_OK)


# RESOURCE TYPE

RESOURCE_TYPE_ENDPOINT_PREFIX = "scrud:resourcetype"
RESOURCE_TYPE_ENDPOINT_DETAIL_NAME = f"{RESOURCE_TYPE_ENDPOINT_PREFIX}-detail"
RESOURCE_TYPE_ENDPOINT_LIST_NAME = f"{RESOURCE_TYPE_ENDPOINT_PREFIX}-list"


@pytest.fixture
def new_resource_type_data():
    return {
        'content': {'type_uri': 'https://schema.org/givenName'},
    }


@pytest.mark.django_db
@scripted_test
def test_resource_type_get_list(regular_login):
    Given.http.get(reverse(RESOURCE_TYPE_ENDPOINT_LIST_NAME))
    Then.http.status_code_is(status.HTTP_200_OK)


@pytest.mark.skip('skipping now for permission issues')
@pytest.mark.django_db
@scripted_test
def test_resource_type_get_detail(regular_login):
    data = ResourceTypeFactory()
    Given.http.get(
        reverse(RESOURCE_TYPE_ENDPOINT_DETAIL_NAME, kwargs={'pk': data.id})
    )
    Then.http.status_code_is(status.HTTP_200_OK)


@pytest.mark.skip(
    'skipping now for "django.core.exceptions.ImproperlyConfigured" error'
)
@pytest.mark.django_db
@scripted_test
def test_resource_type_post(new_resource_data):
    Given.http.post(
        reverse(RESOURCE_TYPE_ENDPOINT_LIST_NAME),
        json.dump(new_resource_data),
        content_type='application/json',
    )
    Then.http.status_code_is(status.HTTP_200_OK)


@pytest.mark.skip('skipping now for permission issues')
@pytest.mark.django_db
@scripted_test
def test_resource_type_put(new_resource_data):
    data_factory = ResourceFactory()

    Given.http.post(
        reverse(
            RESOURCE_TYPE_ENDPOINT_LIST_NAME, kwargs={'pk': data_factory.id}
        ),
        json.dump(new_resource_data),
        content_type='application/json',
    )
    Then.http.status_code_is(status.HTTP_200_OK)
