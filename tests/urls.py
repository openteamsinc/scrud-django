import os

from django.db.utils import OperationalError

from scrud_django.registration import ResourceTypeRegistration

registration_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'scrud-registration.yml'
)

urlpatterns = []

try:
    registration = ResourceTypeRegistration(registration_file)
    urlpatterns.extend(registration.urls)
except OperationalError:
    import logging

    logging.warn(
        "Failed to register resource types! If you're running migrations "
        "this is OK and expected."
    )
