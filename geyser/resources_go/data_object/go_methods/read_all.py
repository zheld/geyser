#!/usr/bin/env python
# coding=utf-8
from geyser.resources_python.methods.abs_method import AbstractMethod


class ReadAllGoMethod( AbstractMethod ):
    def __init__( self, table ):
        super( ReadAllGoMethod, self ).__init__( table, 'ReadAll' )
        self.args = [ table.getIdentifier( ) ]
        self.doc = '# Прочитать строку из базы по первичному ключу со строками таблиц, на которые ссылаются внешние ссылки'

    def getNative( self, classitem ):
        if not self.data.table:
            return
        methoditem = classitem.addClassMethod( self.Name( ), self.getArgsNameList( ) )
        if not self.table.CheckExistsRemoteForeign( ):
            body = '''yield sql_async_one('SELECT {procedure}(' + str({pkey}) + ')')'''.format( procedure = self.procedure,
                                                                                                pkey = self.table.getIdentifier( ).Name( ) )
            methoditem.addBody( body )
        else:
            body = [ ]
            body.append( '''res = yield sql_async_one('SELECT {procedure}(' + str({pkey}) + ')') '''.format( procedure = self.procedure,
                                                                                                             pkey = self.table.getIdentifier( ).Name( ) ) )
            for idx, field in enumerate( self.table.getFields( ) ):
                if field.isForeign( ) and field.isForeignRemote( ):
                    body.append( '''res[{idx}] = yield {service}.{table}.Read(res[{idx}])'''.format( idx = idx,
                                                                                                     service = field.getService( ).Name( ),
                                                                                                     table = field.getDataObject( ).Name( ) ) )
            body.append( 'yield res' )
            methoditem.addBody( body )

    def getNative( self ):
        if not self.data.table:
            return
        self.data.gofile.addImport( "core" )
        func = self.data.gofile.addFunction( self.Name( ) )
        func.addResults( "t *{type}, err error".format( type = self.data.gotype.Name( ) ) )
        func.addArgs( 'id int64' )

        fields = [ ]
        for field in self.data.getFields( ):
            fields.append( "&t." + field.Name( ).capitalize( ) )

        body = '''    t = &{type}<@@>
    row := core.Postgres.QueryRow("SELECT {type_lower}_read($1)", id)
    err = row.Scan({fields})
    if err != nil <@
        core.PublishError("{type_lower}.Read: " + err.Error())
        return
    @>
    return'''.format( type_lower = self.data.Name( ),
                      type = self.data.gotype.Name( ),
                      fields = ', '.join( fields )
                      )
        func.addBody( body )

    def getSqlProcedure( self ):
        fields = [ '{}.{}'.format( self.data.Name( ), fl.Name( ) ) for fl in self.data.getFields( ) ]
        join_block = [ ]

        for field in self.data.getFields( ):
            if field.isForeign( ) and not field.isForeignRemote( ):
                field = field.field
                fields += [ '{}.{}'.format( field.getDataObject( ).Name( ), fl.Name( ) ) for fl in field.getForeignFields( ) ]
                join_block.append( '''LEFT JOIN {join_table}
        ON {join_table}.{foreign} = {table}.{foreign}'''.format( join_table = field.field.getDataObject( ).Name( ),
                                                                 table = self.data.Name( ),
                                                                 foreign = field.Name( ) ) )
        body = '''
CREATE OR REPLACE FUNCTION public.{table}_readall( _id INTEGER )
    RETURNS RECORD
    LANGUAGE plpgsql
AS $function$
DECLARE
    result RECORD;
BEGIN
    SELECT
        {fields}
    FROM
        {table}
    {join_block}
    WHERE
        {table}.{pkey} = _id INTO result;
  RETURN result;
END;
$function$;'''.format( fields = ', '.join( fields ),
                       table = self.data.Name( ),
                       join_block = '\n'.join( join_block ),
                       pkey = self.data.getIdentifier( ).Name( )
                       )
        return body.splitlines( )
