#!/usr/bin/env python
# coding=utf-8
from geyser.resources_go.data_object.go_methods import AbstractMethod


class RemoveListDataGoMethod( AbstractMethod ):
    def __init__( self, data ):
        super( RemoveListDataGoMethod, self ).__init__( data, 'Remove' )

    def getNative( self ):
        self.data.gofile.addImport( "fmt" )
        func = self.data.gofile.addFunction( self.Name( ) )
        func.addArgs( "key {key_type}".format( key_type = self.data.getKeyType( ),
                                               ) )
        func.addResults( "res *{value_type}, err error".format( value_type = self.data.getValueType( ) ) )

        body = '''    if res, ok := {data}_list[key]; ok <@
        delete({data}_list, key)
        return &res, nil
    @>
    return err, error(fmt.Sprintf("not key [%v]", key))'''.format( data = self.data.value_type.Name( ) )
        func.addBody( body )
