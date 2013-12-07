#!/usr/bin/python3.2
__author__ = 'shane'
from collections import namedtuple

#define force-quirk flag modes for DoctypeToken
force_quirks_modes = ("OFF", "ON")
force_quirks_modes = namedtuple("force_quirk_mode", force_quirks_modes)(*range(len(force_quirks_modes)))

#define self_closing_flag for start/end tag tokens
self_closing_modes = ("UNSET", "SET")
self_closing_modes = namedtuple("force_quirk_mode", self_closing_modes)(*range(len(self_closing_modes)))
class Doctype(object):
    def __init__(self,):
        self.name = ""
        self.public_id = ""
        self.system_id = ""
        self.force_quirks_flag = force_quirks_modes.OFF

class StartTag(object):
    def __init__(self, tag_name):
        self.self_closing_flag = self_closing_modes.UNSET
        self.attributes = []
        self.tag_name= tag_name

class StopTag(object):
    def __init__(self, tag_name):
        self.self_closing_flag = self_closing_modes.UNSET
        self.attributes = []
        self.tag_name = tag_name

class Comment(object):
    def __init__(self, data=""):
        self.data = data

class Character(object):
    def __init__(self, data):
        self.data = data