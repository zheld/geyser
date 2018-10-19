#!/usr/bin/env python
# coding=utf-8
from resources_go.data_object.go_methods.abs_method import AbstractMethod


class ListFilter( AbstractMethod ):
    def __init__( self, data ):
        super( ListFilter, self ).__init__( data, 'ListFilter' )

    def getNative( self ):
        if not self.data.table:
            return
        if self.data.getIdentifier().getType() == "TEXT":
            return
        self.data.gofile.addImport( "core" )
        self.data.gofile.addImport( "fmt" )
        self.data.gofile.addImport( "strings" )
        func = self.data.gofile.addFunction( self.Name( ) )

        func.addArgs( 'from *int, limit int, filter_list *[]string' )

        func.addResults( "res []{type}, count int, err error".format( type = self.data.gotype.Name( ) ) )

        fields = [ ]
        for field in self.data.getFields( ):
            fields.append( "&p." + field.Name( ).capitalize( ) )

        body = '''    where_block_list := []string<@@>

    if filter_list != nil <@
        for _, filter := range *filter_list <@
            where_block_list = append(where_block_list, filter)
        @>
    @>

    if from != nil <@
        where_block_list = append(where_block_list, fmt.Sprintf("id > %v", *from))
        //where_block_list = append(where_block_list, fmt.Sprintf("id <= %v", from + limit))
    @>

    limit_block := ""
    if limit != 0 <@
        limit_block = fmt.Sprintf(" LIMIT %v", limit)
    @>

    where_block := ""
    if len(where_block_list) != 0 <@
        where_block = strings.Join(where_block_list, " AND ")
        where_block = "WHERE " + where_block
    @>
    sql := "SELECT {fields} FROM {data} " + where_block + limit_block

    rows, err := core.Postgres.Query(sql)
    if err != nil <@
        core.PublishError("{data}.ListFilter: " + err.Error())
        return res, count, err
    @>

    defer rows.Close()

    for rows.Next() <@
        p := {type}<@@>
        err := rows.Scan({type_fields})
        res = append(res, p)
        if err != nil <@
            core.PublishError("{data}.List: " + err.Error())
            return res, count, err
        @>
        count++
        if *from < p.Id <@
            *from = p.Id
        @>
    @>
    return res, count, err'''.format( type_lower = self.data.Name( ),
                                      type = self.data.gotype.Name( ),
                                      type_fields = ', '.join( fields ),
                                      fields = ", ".join( fl.Name( ) for fl in self.data.getFields( ) ),
                                      data = self.data.Name( )
                                      )
        func.addBody( body )
