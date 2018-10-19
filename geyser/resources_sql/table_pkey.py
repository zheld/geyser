#!/usr/bin/env python
# coding=utf-8
from resources_sql.field import *
from .table import Table
from resources_go.types import go_types

first_exc = "The first in the table is not the primary key !! In the table, the PK must always come first!"

class TableWithPrimaryKey( Table ):
    # Prototype class tibitsy
    # Basic class of creating data access modules that provides initial
    # functionality for accessing the table.
    # Warning: the primary key should always be added first!

    def __init__( self, parent ):
        super( TableWithPrimaryKey, self ).__init__( parent )

    def getPKey( self ):
        pkey = self.items[ 0 ]
        if pkey.isIdentifier( ):
            return pkey
        else:
            raise Exception( first_exc )

    def addPKey( self ):
        name = self.Name( ) + '_id'
        new_field = Field(name, self, go_types.integer, primary = True)
        if len( self.items ) != 0:
            raise Exception( first_exc )
        self.addItem( new_field )
        return new_field

    def GetFieldsWithoutPkey( self ):
        return self.getFields( )[ 1: ]
