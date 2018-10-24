#!/usr/bin/env python
# coding=utf-8
from geyser.resources_go.data_object.go_methods.abs_method import AbstractMethod


class ReadGoMethod( AbstractMethod ):
    def __init__( self, data ):
        super( ReadGoMethod, self ).__init__( data, 'Read' )

    def getNative( self ):
        if not self.data.table:
            return
        self.data.gofile.addImport( "core" )
        func = self.data.gofile.addFunction( self.Name( ) )
        func.addResults( "t {type}, err error".format( type = self.data.gotype.Name( ) ) )
        func.addArgs( 'id int' )

        fields = [ ]
        for field in self.data.getFields( ):
            fields.append( "&t." + field.Name( ).capitalize( ) )

        body = '''    t = {type}<@@>
    row := core.Postgres.QueryRow("SELECT * FROM {table} WHERE id = $1", id)
    err = row.Scan({fields})
    if err != nil <@
        core.PublishError("{table}.Read: " + err.Error())
        return
    @>
    return'''.format( table = self.data.Name( ),
                      type = self.data.gotype.Name( ),
                      fields = ', '.join( fields )
                      )
        func.addBody( body )

    def getSqlProcedure( self ):
        if not self.data.table:
            return
        fields = ', '.join( '{}.{}'.format( self.data.Name( ), fl.Name( ) ) for fl in self.data.getFields( ) )
        body = '''
CREATE OR REPLACE FUNCTION public.{table}_read( _id {type} )
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
    WHERE
        {table}.id = _id INTO result;
  RETURN result;
END;
$function$;'''.format( fields = fields,
                       table = self.data.Name( ),
                       type = self.data.getIdentifier().getType()
                       )
        self.data.sql_file.Write( body.splitlines( ) )
