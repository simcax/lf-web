"""Tests member data retrieval and manipulation - ie. stats"""

import pytest

from lfweb import create_app

from ..members.list import Members


def test_create_member_class_object():
    member_obj = Members()
    assert isinstance(member_obj, object) is True
