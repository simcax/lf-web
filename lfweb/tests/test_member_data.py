"""Tests member data retrieval and manipulation - ie. stats"""

from ..members.list import Members


def test_create_member_class_object():
    """Test the members class yields an object - base test"""
    member_obj = Members()
    assert isinstance(member_obj, object) is True
