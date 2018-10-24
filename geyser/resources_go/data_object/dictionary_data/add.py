#!/usr/bin/env python
# coding=utf-8
from geyser.resources_go.data_object.go_methods.abs_method import AbstractMethod


class AddDictionaryDataGoMethod( AbstractMethod ):
    def __init__( self, data ):
        super( AddDictionaryDataGoMethod, self ).__init__( data, 'Add' )

    def getNative( self ):
        func = self.data.gofile.addFunction( self.Name( ) )
        func.addArgs( "key {key_type}, value {value_type}".format( key_type = self.data.getKeyType( ),
                                                                   value_type = self.data.getValueType( ) ) )

        body = '''    {value}_map[key] = value'''.format( value = self.data.Name()
                                                           )
        func.addBody( body )

