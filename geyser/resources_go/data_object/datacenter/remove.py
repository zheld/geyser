#!/usr/bin/env python
# coding=utf-8
from geyser.resources_go.data_object.go_methods.abs_method import AbstractMethod


class Remove( AbstractMethod ):
    def __init__( self, data ):
        super( Remove, self ).__init__( data, 'Remove' )

    def getNative( self ):
        self.data.gofile.addImport( "fmt" )
        self.data.gofile.addImport( "errors" )
        func = self.data.gofile.addFunction( self.Name() )
        func.addArgs( "id {type}".format( type = self.data.value_type.getIdentifier().getGoType() ) )
        func.addResults( "err error".format( value_type = self.data.getValueType() ) )

        body = '''    _, count := GetById(id)
    if count > 0 <@
        from_indexes_del(id)
        return nil
    @>
    msg := fmt.Sprintf("{data}: {value_type} id: [%v] not found", id)
    core.PublishError(msg)
    return errors.New(msg)'''.format( value_type = self.data.value_type.Name(),
                                      data = self.data.Name(),

                                      )
        func.addBody( body )
