#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
r"""JSON File Manager

Update: 2015-03-23 12:00:00
Author: vbem@163.com
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import json

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# classes

class JsonFile:
    r"""JSON file manager.
    """
    sPath       = None  # path of JSON file
    oDataCache  = None  # cache for data, default to not read yet flag
    
    def __init__(self, sPath):
        r"""Initialize with JSON file path.
        """
        self.sPath = sPath
    
    def __repr__(self):
        r"""Representation.
        """
        return '{}({!r})'.format(self.__class__.__name__, self.sPath)

    def getPath(self):
        r"""Get path.
        """
        return self.sPath

    def load(self, bCache=True):
        r"""Get data from file.
        """
        if self.oDataCache is None or not bCache:
            with open(self.sPath) as f:
                self.oDataCache = json.load(fp=f)
        return self.oDataCache
        
    def dump(self, oData):
        r"""Set date to file.
        """
        with open(self.sPath, 'w') as f:
            json.dump(obj=oData, fp=f, ensure_ascii=False, indent=4)
        self.oDataCache = oData # set cache

