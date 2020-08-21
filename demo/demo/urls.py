import os

from django.urls import path

from scrud_django.registration import ResourceTypeRegistration

from . import views

registration_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'scrud-registration.yml'
)

urlpatterns = [
    path("services", views.ServiceCatalog.as_view()),
    path("json-schema/PartnerProfile", views.PartnerProfileSchema.as_view()),
    path("json-ld/PartnerProfile", views.PartnerProfileContext.as_view()),
    path("examples/partner-profile", views.ExamplePartnerProfile.as_view()),
]

registration = ResourceTypeRegistration(registration_file)
urlpatterns.extend(registration.urls)
