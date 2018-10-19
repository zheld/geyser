#!/usr/bin/env python
# coding=utf-8
from resources_go.data_object.go_methods.abs_method import AbstractMethod


class InsertGoMethod( AbstractMethod ):
    def __init__( self, data ):
        super( InsertGoMethod, self ).__init__( data, 'Insert' )
        self.args = [ fl for fl in data.getFields( ) if not fl.isAuto( ) ]

    def getNative( self ):
        if not self.data.table:
            return

        # return instance
        func = self.data.gofile.addFunction( self.Name( ) + "ReturnInstance" )
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
        func.addResults( "{type}, error".format( type = self.data.gotype.Name( ) ) )

        body = '''    newi := {type}<@
{vars}
    @>
    row := core.Postgres.QueryRow("SELECT {table}_insert({inside_procedure_args})", {procedure_args})
    err := row.Scan(&newi.Id)
    if err != nil <@
        return newi, err
    @>
    return newi, nil'''.format( table = self.data.Name( ),
                               inside_procedure_args = inside_procedure_args,
                               procedure_args = procedure_args,
                               data = self.data.Name( ),
                               type = self.data.gotype.Name( ),
                               vars = vars,
                               or_read = "_or_read" if (self.data.unique_field_set or self.data.getIdentifier( ).isAuto( )) else ""
                               )
        func.addBody( body )

        # return id
        func = self.data.gofile.addFunction( self.Name( ) )
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
        func.addResults( "_id int, err error" )

        body = '''    row := core.Postgres.QueryRow("SELECT {table}_insert({inside_procedure_args})", {procedure_args})
    err = row.Scan(&_id)
    if err != nil <@
        return _id, err
    @>
    return _id, nil'''.format( table = self.data.Name( ),
                               inside_procedure_args = inside_procedure_args,
                               procedure_args = procedure_args
                               )
        func.addBody( body )

    def getSqlProcedure( self ):
        if not self.data.table:
            return
        args = ', '.join( 'p_' + fl.Name( ) for fl in self.args )
        fields = ', '.join( fl.Name( ) for fl in self.args )
        args_type = ', '.join( 'p_{} {}'.format( fl.Name( ), fl.type ) for fl in self.args )
        body = '''
CREATE OR REPLACE FUNCTION public.{table}_insert( {args_type} )
    RETURNS {type}
    LANGUAGE plpgsql
AS $function$
DECLARE
  result {type};
BEGIN
  INSERT INTO {table} ({fields})
      VALUES ({args}) RETURNING {table}.id INTO result;
  RETURN result;
END;
$function$;'''.format( procedure = self.procedure,
                       args_type = args_type,
                       table = self.data.Name( ),
                       args = args,
                       fields = fields,
                       type = self.data.getIdentifier().getType()
                       )
        self.data.sql_file.Write( body.splitlines( ) )
