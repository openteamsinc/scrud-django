import os

from django.db.utils import OperationalError
from django.urls import path

from scrud_django.registration import ResourceTypeRegistration

from . import views

registration_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'scrud-registration.yml'
)

urlpatterns = [
    path("services", views.ServiceCatalog.as_view()),
    path(
        "demo/json-schema/PartnerProfile", views.PartnerProfileSchema.as_view()
    ),
    path("demo/json-ld/PartnerProfile", views.PartnerProfileContext.as_view()),
    path(
        "demo/examples/PartnerProfile", views.ExamplePartnerProfile.as_view()
    ),
]

try:
    registration = ResourceTypeRegistration(registration_file)
    urlpatterns.extend(registration.urls)
except OperationalError:
    import logging

    logging.warn(
        "Failed to register resource types! If you're running migrations "
        "this is OK and expected."
    )
