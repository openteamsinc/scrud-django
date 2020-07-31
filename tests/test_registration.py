import pytest
import yaml
from safetydance_test import Given, Then, scripted_test

from scrud_django.registration import ResourceTypeRegistration

from .fixtures import *  # noqa: F403, F401
from .steps import *  # noqa: F403, F401


@pytest.mark.django_db
@scripted_test
def test_registration(http_static_server):
    register_name = 'partner-profiles'

    with open(REGISTRATION_FILE_PATH) as f:  # noqa: F405
        registration_data_source = yaml.load(f, Loader=yaml.FullLoader)

    registration = ResourceTypeRegistration(
        REGISTRATION_FILE_PATH  # noqa: F405
    )
    result = registration.resource_type_list[0]

    Given.an_registration_data(register_name, registration_data_source)
    Then.check_registration_results(register_name, result)
