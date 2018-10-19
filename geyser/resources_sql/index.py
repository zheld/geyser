#!/usr/bin/env python
# coding=utf-8
from item import *


class Index( Item ):
    def __init__( self, table, *fields ):
        super( Index, self ).__init__( '', table )
        name = '{table}_{fields}_index'.format( table = table.Name( ),
                                                fields = '_'.join( fl.Name( ) for fl in fields ) )
        self._name = name
        self.items = fields

    def getFields( self ):
        return self.items

    def getTable( self ):
        return self.parent

    def getService( self ):
        return self.GetTable( ).getService( )

    def isUnique( self ):
        return isinstance( self, UniqueIndex )

    def Serialize( self ):
        idxjson = { }
        idxjson[ 'name' ] = self.Name( )
        idxjson[ 'table' ] = self.getTable( ).Name( )
        idxjson[ 'unique' ] = self.isUnique( )
        idxjson[ 'fields' ] = [ fl.Name( ) for fl in self.getFields( ) ]
        return idxjson


class UniqueIndex( Index ):
    def __init__( self, table, *fields ):
        super( UniqueIndex, self ).__init__( table, *fields )
