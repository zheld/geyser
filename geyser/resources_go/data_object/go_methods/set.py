#!/usr/bin/env python
# coding=utf-8
from geyser.resources_go.data_object.go_methods.abs_method import AbstractMethod
from geyser.resources_go.types import go_types


class UpdateByGoMethod( AbstractMethod ):
    def __init__( self, data ):
        super( UpdateByGoMethod, self ).__init__( data, 'Set' )
        self.args = [ fl for fl in data.getFields( ) if not fl.isAuto( ) and not fl.isIdentifier( ) ]

    def getNative( self ):
        if not self.data.table or not self.data.getIdentifier():
            return
        for field in self.args:
            name = field.Name( ).capitalize( )
            func = self.data.gotype.addMethod( "Set{}".format( name ) )

            func.addArgs( "{field} {type}".format( field = field.Name( ),
                                                            type = go_types.go_converter(field.getType())
                                                            ) )
            func.addResults( "error" )

            body = '''    sql := "UPDATE {data} SET {field} = $1 WHERE id = $2"
    _, err := core.Postgres.Exec(sql, {field}, self.Id)
    if err != nil <@
        return err
    @>
    self.{gofield} = {field}
    return nil'''.format( data = self.data.Name( ),
                          field = field.Name( ),
                          gofield = name
                          )

            func.addBody( body )
