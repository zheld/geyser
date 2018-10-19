#!/usr/bin/env python
# coding=utf-8
from resources_go.data_object.go_methods.abs_method import AbstractMethod


class Delete( AbstractMethod ):
    def __init__( self, data ):
        super( Delete, self ).__init__( data, 'Delete' )

    def getNative( self ):
        if not self.data.table:
            return
        self.data.gofile.addImport( "core" )
        func = self.data.gofile.addFunction( self.Name( ) )

        func.addArgs( 'id {type}'.format(type = self.data.getIdentifier( ).getGoType( )) )
        func.addResults( "error" )

        body = '''    sql := "DELETE FROM {data} WHERE id = $1"
    _, err := core.Postgres.Exec(sql, id)
    return err'''.format( data = self.data.Name( ) )
        func.addBody( body )
