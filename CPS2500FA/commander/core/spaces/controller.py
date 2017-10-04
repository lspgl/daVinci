import importlib
import sys
import os


class Controller:

    def __init__(self):
        # Initialize cache for spaces
        self.spaces = {}

    def initSpace(self, name, space):
        self.spaces[name] = space
