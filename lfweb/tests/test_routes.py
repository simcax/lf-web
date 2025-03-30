"""Tests to ensure that the routes are working as expected."""


def test_memberships_endpoint(client):
    """Test the memberships endpoint"""
    response = client.get("/memberships")
    assert response.status_code == 200
    assert b"Medlemskab" in response.data


def test_doorcount_endpoint(client):
    """Test the doorcount endpoint"""
    response = client.get("/doorcount")
    assert response.status_code == 200
    assert b"Tid siden indgang" in response.data


def test_membercount_endpoint(client):
    """Test the membercount endpoint"""
    response = client.get("/membercount")
    assert response.status_code == 200
    assert b"medlemmer i alt" in response.data
