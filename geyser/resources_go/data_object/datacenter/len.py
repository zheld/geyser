#!/usr/bin/env python
# coding=utf-8
from geyser.resources_go.data_object.go_methods.abs_method import AbstractMethod


class Len( AbstractMethod ):
    def __init__( self, data ):
        super( Len, self ).__init__( data, 'Len' )

    def getNative( self ):
        func = self.data.gofile.addFunction( self.Name( ) )
        func.addResults( "int" )
        body = '''    return len(index_{first_index})'''.format( first_index = self.data.getIndexes( )[ 0 ].Name( ) )
        func.addBody( body )
