import os

# from django.db.utils import OperationalError
from django.urls import include, path

# from scrud_django.registration import ResourceTypeRegistration

registration_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'scrud-registration.yml'
)

urlpatterns = [
    path("", include("scrud_django.urls")),
]

# try:
# registration = ResourceTypeRegistration(registration_file)
# urlpatterns.extend(registration.urls)
# except OperationalError:
# import logging

# logging.warn(
# "Failed to register resource types! If you're running migrations "
# "this is OK and expected."
# )
