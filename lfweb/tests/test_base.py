"""
Basic tests for the base app
"""


def test_instantiate(redis_container, client):  # pylint: disable=unused-argument
    """Test the App loads and there is access to the main route"""
    response = client.get("/")
    assert response.status_code == 200
