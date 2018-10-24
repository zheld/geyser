#!/usr/bin/env python
# coding=utf-8
from geyser.resources_go.data_object.go_methods.abs_method import AbstractMethod


class AddListDataGoMethod( AbstractMethod ):
    def __init__( self, data ):
        super( AddListDataGoMethod, self ).__init__( data, 'Add' )

    def getNative( self ):
        func = self.data.gofile.addFunction( self.Name( ) )
        func.addArgs( "value *{value_type}".format( value_type = self.data.getValueType( ) ) )

        body = '''    {value}_list = append({value}_list, value)'''.format( value = self.data.value_type.Name()
                                                           )
        func.addBody( body )

