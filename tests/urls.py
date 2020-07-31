import os

from scrud_django.registration import ResourceTypeRegistration

registration_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'scrud-registration.yml'
)

urlpatterns = []

registration = ResourceTypeRegistration(registration_file)
urlpatterns.extend(registration.urls)
