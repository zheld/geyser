#!/usr/bin/env python
# coding=utf-8
from resources_go.data_object.go_methods.abs_method import AbstractMethod


class GetId( AbstractMethod ):
    def __init__( self, data ):
        super( GetId, self ).__init__( data, 'GetId' )
        # self.args = [ fl for fl in data.getFields( ) if not fl.isAuto( ) and not fl.isIdentifier( ) ]
        self.args = self.data.unique_field_set

    def getNative( self ):
        if not self.data.table and not self.data.unique_field_set:
            return
        if not self.data.getIdentifier().isAuto():
            return

        func = self.data.gofile.addFunction( self.Name() )
        func.addResults( "_id int, err error" )
        if self.data.has_get_id:
            func.addComment( "//!api get_{data}_id".format( data = self.data.Name() ) )

        method_args_list = [ ]
        inside_procedure_args_list = [ ]
        procedure_args_list = [ ]
        for number, fl in enumerate( self.args ):
            method_args_list.append( "{name} {type}".format( name = fl.Name(), type = fl.getGoType() ) )
            inside_procedure_args_list.append( "${number}".format( number = number + 1 ) )
            procedure_args_list.append( fl.Name() )

        method_args = ", ".join( method_args_list )
        inside_procedure_args = ", ".join( inside_procedure_args_list )
        procedure_args = ", ".join( procedure_args_list )

        func.addArgs( method_args )

        body = '''    row := core.Postgres.QueryRow("SELECT {data}_get_id({inside_procedure_args})", {procedure_args})
    err = row.Scan(&_id)
    if err != nil <@
        core.PublishError("{data}.GetId: " + err.Error())
        return _id, err
    @>
    return _id, nil'''.format( data = self.data.Name(),
                              type = self.data.gotype.Name(),
                              inside_procedure_args = inside_procedure_args,
                              procedure_args = procedure_args
                              )
        func.addBody( body )
    def getSqlProcedure( self ):
        if not self.data.table:
            return
        if not self.data.getIdentifier().isAuto():
            return
        args = ', '.join( 'p_' + fl.Name( ) for fl in self.args )
        fields = ', '.join( fl.Name( ) for fl in self.args )
        args_type = ', '.join( 'p_{} {}'.format( fl.Name( ), fl.type ) for fl in self.args )
        where_fields = " AND ".join( "{field} = p_{field}".format( field = fl.Name( ) ) for fl in self.args )

        body = '''
CREATE OR REPLACE FUNCTION public.{table}_get_id( {args_type} )
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
DECLARE
  result INTEGER;
BEGIN
  SELECT
    id
  FROM
    {table}
  WHERE
    {where_fields} INTO result;
  RETURN result;
END;
$function$;'''.format( args_type = args_type,
                       table = self.data.Name( ),
                       args = args,
                       fields = fields,
                       where_fields = where_fields
                       )
        self.data.sql_file.Write( body.splitlines( ) )
