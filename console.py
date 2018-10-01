# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 08:13:58 2018

@author: install
"""

from code import InteractiveConsole
from imp import new_module
 
class Console(InteractiveConsole):
 
    def __init__(self, names=None):
        names = names or {}
        names['console'] = self
        InteractiveConsole.__init__(self, names)
        self.superspace = new_module('superspace')
 
    def enter(self, source):
        source = self.preprocess(source)
        self.runcode(source)
 
    @staticmethod
    def preprocess(source):
        return source
 
console = Console()