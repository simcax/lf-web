"""
Tests for image endpoints
"""


def test_get_logo(redis_container, client):
    """
    Test to retrieve the logo image
    """
    response = client.get("/static/images/logo.png")
    assert response.status_code == 200
