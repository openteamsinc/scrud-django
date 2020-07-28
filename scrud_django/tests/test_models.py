import pytest
from safetydance_test import Given, Then, scripted_test

from .factories import ResourceFactory, ResourceTypeFactory
from .steps import *  # noqa: F403, F401


@pytest.mark.django_db
@scripted_test
def test_resource():
    """Resource test."""
    Given.an_instance_named('resource', ResourceFactory())
    Then.is_valid_resource('resource')


@pytest.mark.django_db
@scripted_test
def test_resource_type():
    """Resource test."""
    Given.an_instance_named('resource_type', ResourceTypeFactory())
    Then.is_valid_resource_type('resource_type')
