#!/usr/bin/env python
# coding=utf-8
from geyser.resources_go.data_object.go_methods.abs_method import AbstractMethod


class List( AbstractMethod ):
    def __init__( self, data ):
        super( List, self ).__init__( data, 'List' )

    def getNative( self ):
        if not self.data.table:
            return
        self.data.gofile.addImport( "core" )
        self.data.gofile.addImport( "fmt" )
        func = self.data.gofile.addFunction( self.Name( ) )

        func.addResults( "res []{type}, err error".format( type = self.data.gotype.Name( ) ) )

        fields = [ ]
        for field in self.data.getFields( ):
            fields.append( "&p." + field.Name( ).capitalize( ) )

        body = '''    sql := "SELECT {fields} FROM {data}"

    rows, err := core.Postgres.Query(sql)
    if err != nil <@
        core.PublishError("{data}.List: " + err.Error())
        return res, err
    @>

    defer rows.Close()

    for rows.Next() <@
        p := {type}<@@>
        err := rows.Scan({type_fields})
        res = append(res, p)
        if err != nil <@
            core.PublishError("{data}.List: " + err.Error())
            return res, err
        @>
    @>
    return res, err'''.format( type_lower = self.data.Name( ),
                               type = self.data.gotype.Name( ),
                               type_fields = ', '.join( fields ),
                               fields = ", ".join( fl.Name( ) for fl in self.data.getFields( ) ),
                               data = self.data.Name( )
                               )
        func.addBody( body )
