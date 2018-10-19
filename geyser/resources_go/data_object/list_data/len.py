#!/usr/bin/env python
# coding=utf-8
from resources_go.data_object.go_methods.abs_method import AbstractMethod


class LenListDataGoMethod( AbstractMethod ):
    def __init__( self, data ):
        super( LenListDataGoMethod, self ).__init__( data, 'Len' )

    def getNative( self ):
        func = self.data.gofile.addFunction( self.Name( ) )
        func.addResults( "int" )
        body = '''    return len({data}_list)'''.format( data = self.data.value_type.Name( )
                                                         )
        func.addBody( body )
