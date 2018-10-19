#!/usr/bin/env python
# coding=utf-8
from generator.FSItem.directory import Directory
from generator.Python.pyfile import PyFile


class Package( Directory ):
    def __init__( self, name, parent=None ):
        super( Package, self ).__init__( name, parent )
        self.addPyFile( '__init__' )

    def addPackage( self, name ):
        pack = Package( name, self )
        self.addItem( pack )
        return pack

