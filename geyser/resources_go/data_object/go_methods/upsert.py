#!/usr/bin/env python
# coding=utf-8
from resources_go.data_object.go_methods.abs_method import AbstractMethod


class UpsertGoMethod( AbstractMethod ):
    def __init__( self, data ):
        super( UpsertGoMethod, self ).__init__( data, 'Upsert' )
        self.args = [ fl for fl in data.getFields( ) if not fl.isAuto( ) ]

    def getNative( self ):
        if not self.data.table:
            return
        # if not self.data.getIdentifier().isAuto():
        #     return
        func = self.data.gofile.addFunction( self.Name( ) + "ReturnInstance" )
        func.addResults( "{type}, error".format( type = self.data.gotype.Name( ) ) )

        method_args_list = [ ]
        inside_procedure_args_list = [ ]
        procedure_args_list = [ ]
        vars_list = [ ]
        for number, fl in enumerate( self.args ):
            method_args_list.append( "{name} {type}".format( name = fl.Name( ), type = fl.getGoType( ) ) )
            inside_procedure_args_list.append( "${number}".format( number = number + 1 ) )
            procedure_args_list.append( fl.Name( ) )
            vars_list.append( "{field_upper}: {field},".format( field_upper = fl.Name( ).capitalize( ),
                                                                field = fl.Name( ) ) )

        method_args = ", ".join( method_args_list )
        inside_procedure_args = ", ".join( inside_procedure_args_list )
        procedure_args = ", ".join( procedure_args_list )
        vars = "\n".join( "        " + var for var in vars_list )

        func.addArgs( method_args )

        body = '''    res := {type}<@
{vars}
    @>
    row := core.Postgres.QueryRow("SELECT {data}_upsert({inside_procedure_args})", {procedure_args})
    err := row.Scan(&res.Id)
    if err != nil <@
        core.PublishError("{data}.InsertRead: " + err.Error())
        return res, err
    @>
    return res, nil'''.format( data = self.data.Name( ),
                               type = self.data.gotype.Name( ),
                               inside_procedure_args = inside_procedure_args,
                               procedure_args = procedure_args,
                               vars = vars)
        func.addBody( body )

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

        body = '''    row := core.Postgres.QueryRow("SELECT {data}_upsert({inside_procedure_args})", {procedure_args})
    err = row.Scan(&_id)
    if err != nil <@
        core.PublishError("{data}.InsertRead: " + err.Error())
        return _id, err
    @>
    return _id, nil'''.format( data = self.data.Name( ),
                               type = self.data.gotype.Name( ),
                               inside_procedure_args = inside_procedure_args,
                               procedure_args = procedure_args,
                               vars = vars)
        func.addBody( body )

    def getSqlProcedure( self ):
        if not self.data.table:
            return
        if not self.data.getIdentifier().isAuto():
            return
        args = ', '.join( 'p_' + fl.Name( ) for fl in self.args )
        fields = ', '.join( fl.Name( ) for fl in self.args )
        args_type = ', '.join( 'p_{} {}'.format( fl.Name( ), fl.type ) for fl in self.args )
        where_fields = " AND ".join( "{field} = p_{field}".format( field = fl.Name( ) ) for fl in self.data.unique_field_set )
        set_fields = ", ".join( "{field} = p_{field}".format( field = fl.Name( ) ) for fl in self.args )

        body = '''
CREATE OR REPLACE FUNCTION public.{table}_upsert( {args_type} )
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
  ELSE 
    UPDATE {table} SET {set_fields} WHERE id = result;
  END IF;
  
  RETURN result;

END;
$function$;'''.format( args_type = args_type,
                       table = self.data.Name( ),
                       args = args,
                       fields = fields,
                       where_fields = where_fields,
                       set_fields = set_fields
                       )
        self.data.sql_file.Write( body.splitlines( ) )
