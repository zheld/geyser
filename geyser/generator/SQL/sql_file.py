#!/usr/bin/env python
# coding=utf-8
from generator.FSItem.file import File


class SQLFile( File ):
    def __init__( self, name, parent=None, only_create=False ):
        super( SQLFile, self ).__init__( name + '.sql', parent, only_create = only_create )
