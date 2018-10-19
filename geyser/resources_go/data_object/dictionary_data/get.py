#!/usr/bin/env python
# coding=utf-8
from resources_go.data_object.go_methods.abs_method import AbstractMethod


class GetDictionaryDataGoMethod( AbstractMethod ):
    def __init__( self, data ):
        super( GetDictionaryDataGoMethod, self ).__init__( data, 'Get' )

    def getNative( self ):
        self.data.gofile.addImport( "fmt" )
        self.data.gofile.addImport( "errors" )
        func = self.data.gofile.addFunction( self.Name( ) )
        func.addArgs( "key {key_type}".format( key_type = self.data.getKeyType( ),
                                               ) )
        func.addResults( "res *{value_type}, err error".format( value_type = self.data.getValueType( ) ) )

        body = '''    if res, ok := {data}_map[key]; ok <@
        return &res, nil
    @>
    return res, errors.New(fmt.Sprintf("not key [%v]", key))'''.format( data = self.data.Name() )
        func.addBody( body )
