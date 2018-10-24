#!/usr/bin/env python
# coding=utf-8
from geyser.resources_go.types import go_types
from geyser.item import *


class Field( Item ):
    def __init__( self, name, table, type, default=None, primary=False, const=False, field=None, auto=None, is_array=False ):
        super( Field, self ).__init__( name, table )
        self.type = type
        self.default = default
        self.const = const
        self.field = field
        self.auto = auto
        self.primary = primary
        self.is_array = is_array
        self.history = False

    def getDataObject( self ):
        return self.parent

    def getForeignTable( self ):
        return self.field.getDataObject( )

    def getService( self ):
        return self.getDataObject( ).getService( )

    def getForeignService( self ):
        return self.field.getService( )

    def isData(self):
        from geyser.resources_go.data_object.data import GoDataObject
        return isinstance(self.field, GoDataObject)

    def isForeign( self ):
        return bool( self.field )

    def isForeignOneToMany( self ):
        return "[]" in self.getType( )

    def isForeignRemote( self ):
        service = self.getService( )
        foreign_service = self.getForeignService( )
        return not service.Name( ) == foreign_service.Name( )

    def getForeignFields( self ):
        if self.isForeign( ) is not None:
            return self.getForeignTable( ).getFields( )
        else:
            return None

    def getType( self ):
        return self.type

    def getGoType( self ):
        return go_types.go_converter(self.type) if not self.isData() else self.field.getFullType()

    def getDefault( self ):
        return self.default

    def getNameQuotes( self ):
        if self.type in [go_types.text]:
            return ''' "'" + str({}) + "'" '''.format( self.Name( ) )
        return 'str({})'.format( self.Name( ) )

    def isConst( self ):
        return self.const

    def isIdentifier( self ):
        return self.primary

    def isAutoIdentifier( self ):
        if self.primary:
            return self.isAuto( )
        else:
            raise Exception( "это не первичный ключ!!" )

    def isAuto( self ):
        return bool( self.auto )

    def hasHistory( self ):
        return self.history

    def setHistory( self ):
        self.history = True

    def Serialize( self ):
        fljson = { }
        fljson[ 'name' ] = self.Name( )
        fljson[ 'type' ] = self.getType( )
        fljson[ 'pkey' ] = self.isIdentifier( )
        fljson[ '_default' ] = self.getDefault( )
        if self.isForeign( ) and self.isForeignRemote( ) is False:
            foreign = { }
            foreign[ 'table' ] = self.field.getDataObject( ).Name( )
            foreign[ 'name' ] = self.field.Name( )
        else:
            foreign = None
        fljson[ 'foreign' ] = foreign
        return fljson
