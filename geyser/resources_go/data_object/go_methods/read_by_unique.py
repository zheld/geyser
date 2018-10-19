#!/usr/bin/env python
# coding=utf-8
from resources_go.data_object.go_methods.abs_method import AbstractMethod


class ReadByUnique( AbstractMethod ):
    def __init__( self, data ):
        super( ReadByUnique, self ).__init__( data, 'ReadByUnique' )
        self.args = [ field for field in self.data.unique_field_set ]

    def getNative( self ):
        if not self.data.table:
            return
        self.data.gofile.addImport( "core" )
        func = self.data.gofile.addFunction( self.Name() )
        func.addResults( "t {type}, err error".format( type = self.data.gotype.Name() ) )
        func.addArgs( ", ".join( "{name} {type}".format( name = field.Name(), type = field.getGoType() ) for field in self.args ) )

        fields = [ ]
        for field in self.data.getFields():
            fields.append( "&t." + field.Name().capitalize() )

        body = '''    t = {type}<@@>
    row := core.Postgres.QueryRow("SELECT * FROM {table} WHERE {where_list}", {param_list})
    err = row.Scan({fields})
    if err != nil <@
        core.PublishError("{table}.{methodname}: " + err.Error())
        return
    @>
    return'''.format( table = self.data.Name(),
                      type = self.data.gotype.Name(),
                      fields = ', '.join( fields ),
                      param_list = ", ".join( field.Name() for field in self.args ),
                      methodname = self.Name(),
                      where_list = " AND ".join( "{field} = ${num}".format( field = field.Name(), num = num + 1 ) for num, field in enumerate(self.args) )
                      )
        func.addBody( body )

    def getSqlProcedure( self ):
        if not self.data.table:
            return
        fields = ', '.join( '{}.{}'.format( self.data.Name(), fl.Name() ) for fl in self.data.getFields() )
        body = '''
CREATE OR REPLACE FUNCTION public.{table}_read_by_unique( {param} )
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
        {where_list} INTO result;
  RETURN result;
END;
$function$;'''.format( fields = fields,
                       table = self.data.Name(),
                       param = ", ".join( "_{name} {type}".format( name = ord_sequence.Name(), type = ord_sequence.getType() ) for ord_sequence in self.args ),
                       where_list = " AND ".join( "{ord_sequence} = _{ord_sequence}".format( ord_sequence = ord_sequence.Name() ) for ord_sequence in self.args )
                       )
        self.data.sql_file.Write( body.splitlines() )
