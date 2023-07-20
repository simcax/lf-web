import pytest

from lfweb import create_app


def test_instantiate(redis_container, client):
    response = client.get("/")
    assert response.status_code == 200
