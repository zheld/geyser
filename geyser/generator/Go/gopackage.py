#!/usr/bin/env python
# coding=utf-8
from geyser.generator.FSItem.directory import Directory


class GoPackage( Directory ):
    def __init__( self, name, parent=None ):
        super( GoPackage, self ).__init__( name, parent )

