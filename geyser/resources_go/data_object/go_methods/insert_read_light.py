#!/usr/bin/env python
# coding=utf-8
from geyser.resources_go.data_object.go_methods.abs_method import AbstractMethod


class InsertReadGoLight( AbstractMethod ):
    def __init__( self, data ):
        super( InsertReadGoLight, self ).__init__( data, 'InsertReadLight' )
        self.args = [ fl for fl in self.data.unique_field_set ]

    def getNative( self ):
        if not self.data.table:
            return
        # if not self.data.getIdentifier().isAuto():
        #     return

        # return id
        func = self.data.gofile.addFunction( self.Name( ) )
        func.addResults( "_id int, err error".format( type = self.data.gotype.Name( ) ) )

        method_args_list = [ ]
        inside_procedure_args_list = [ ]
        procedure_args_list = [ ]
        for number, fl in enumerate( self.args ):
            method_args_list.append( "{name} {type}".format( name = fl.Name( ), type = fl.getGoType( ) ) )
            inside_procedure_args_list.append( "${number}".format( number = number + 1 ) )
            procedure_args_list.append( fl.Name( ) )

        method_args = ", ".join( method_args_list )
        inside_procedure_args = ", ".join( inside_procedure_args_list )
        procedure_args = ", ".join( procedure_args_list )

        func.addArgs( method_args )

        body = '''    row := core.Postgres.QueryRow("SELECT {data}_insert{or_read}_light({inside_procedure_args})", {procedure_args})
    err = row.Scan(&_id)
    if err != nil <@
        core.PublishError("{data}.InsertReadLight: " + err.Error())
        return _id, err
    @>
    return _id, nil'''.format( data = self.data.Name( ),
                               type = self.data.gotype.Name( ),
                               inside_procedure_args = inside_procedure_args,
                               procedure_args = procedure_args,
                               vars = vars,
                               or_read = "_or_read" if (self.data.unique_field_set or self.data.getIdentifier().isAuto()) else ""
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
CREATE OR REPLACE FUNCTION public.{table}_insert_or_read_light( {args_type} )
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
  IF result IS NULL THEN
    INSERT INTO {table} ({fields}) VALUES ({args}) RETURNING id INTO result;
  END IF;
  RETURN result;
END;
$function$;'''.format( args_type = args_type,
                       table = self.data.Name( ),
                       args = args,
                       fields = fields,
                       where_fields = where_fields
                       )
        self.data.sql_file.Write( body.splitlines( ) )
