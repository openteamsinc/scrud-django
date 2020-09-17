import json
import os
from http import server
from multiprocessing import Process

import pytest

from .factories import UserFactory

__all__ = [
    'ROOT_PATH',
    'DATA_PATH',
    'regular_login',
    'admin_login',
    'http_static_server',
    'partner_profile_post_data',
]

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT_PATH, 'data')


@pytest.mark.django_db
@pytest.fixture
def regular_login():
    return UserFactory()


@pytest.mark.django_db
@pytest.fixture
def admin_login():
    return UserFactory(is_staff=True)


def http_process_server():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    os.chdir(path)
    server_address = ('localhost', 8123)
    httpd = server.HTTPServer(server_address, server.SimpleHTTPRequestHandler)
    httpd.serve_forever()


@pytest.yield_fixture
def http_static_server():
    p = Process(target=http_process_server, args=())
    p.start()

    yield

    p.join(timeout=1)
    p.kill()


@pytest.fixture
def partner_profile_post_data():
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'static',
        'post_partner_profile.json',
    )
    with open(path, 'r') as f:
        return json.loads(f.read())
