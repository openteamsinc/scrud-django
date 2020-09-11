import importlib
import os

# from django.db.utils import OperationalError
from django.urls import include, path

from scrud_django import registration

registration_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'scrud-registration.yml'
)

urlpatterns = [
    path("", include("scrud_django.urls")),
]

urlpatterns.extend(
    registration.resource_types(
        registration.json_resource_type(
            resource_type_uri="tests://PartnerProfiles",
            revision="1",
            slug="partner-profiles",
            schema_func=lambda: importlib.resources.read_text(
                "tests.static.json_schema", "PartnerProfile"
            ),
            context_func=lambda: importlib.resources.read_text(
                "tests.static.json_ld", "PartnerProfile"
            ),
        ),
    )
)
