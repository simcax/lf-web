"""Module for handling the memberlist from ForeningLet"""

from foreninglet_data.api import ForeningLet
from foreninglet_data.memberlist import Memberlist


class Memberdata:
    """The members class provides methods for handling the members list"""

    initialized = False

    def __init__(self):
        """Setup the member list"""
        fl_obj = ForeningLet()
        memberlist = fl_obj.get_memberlist()
        self.members = Memberlist(memberlist)
