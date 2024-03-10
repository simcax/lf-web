"""Tests member data retrieval and manipulation - ie. stats"""

import pytest

from ..members.list import Memberdata


def test_create_member_class_object():
    """Test the members class yields an object - base test"""
    member_obj = Memberdata()
    assert isinstance(member_obj, object) is True


@pytest.mark.vcr()
def test_member_count():
    """Test that we can retrieve a member count"""
    memberdata = Memberdata()
    assert memberdata.members.member_count >= 1


@pytest.mark.vcr()
def test_members_total():
    """Test that we can retrieve a member count"""
    memberdata = Memberdata()
    assert memberdata.members.member_count >= 1
