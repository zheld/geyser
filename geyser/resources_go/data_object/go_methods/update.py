#!/usr/bin/env python
# coding=utf-8
from geyser.resources_go.data_object.go_methods.abs_method import AbstractMethod


class UpdateGoMethod( AbstractMethod ):
    def __init__( self, data ):
        super( UpdateGoMethod, self ).__init__( data, 'Update' )
        self.args = [ fl for fl in data.getFields( ) if not fl.isAuto( ) ]

    def getNative( self ):
        if not self.data.table:
            return
        func = self.data.gotype.addMethod( self.Name( ) )
        procedure_args_list = [ ]
        set_block_list = [ ]
        nmb = None
        for number, fl in enumerate( self.args ):
            procedure_args_list.append( "self.{field}".format( field = fl.Name( ).capitalize( ) ) )

            set_block_list.append( "${number}".format( number = number + 1 ) )
            nmb = number

        set_block = ", ".join( set_block_list )
        args = ", ".join( procedure_args_list )
        # func.addArgs( "{data} *{type}".format( data = self.data.Name( ),
        #                                        type = self.data.typeName ) )
        func.addResults( "error" )

        body = '''    sql := "SELECT {data}_update({set_block}, ${id_number})"
    _, err := core.Postgres.Exec(sql, {args}, self.Id)
    return err'''.format( data = self.data.Name( ),
                          set_block = set_block,
                          id_number = nmb + 2,
                          args = args )
        func.addBody( body )

    def getSqlProcedure( self ):
        if not self.data.table or not self.data.getIdentifier():
            return
        args_list = [ ]
        fields_list = [ ]
        args_type_list = [ ]
        set_block_list = [ ]
        for fl in self.args:
            args_list.append( "p_{}".format( fl.Name( ) ) )
            fields_list.append( fl.Name( ) )
            args_type_list.append( "p_{} {}".format( fl.Name( ), fl.getType( ) ) )
            set_block_list.append( "    {field} = p_{field}".format( field = fl.Name( ) ) )

        body = '''
CREATE OR REPLACE FUNCTION public.{table}_update( {args_type}, _id {type} )
    RETURNS VOID
LANGUAGE plpgsql
AS $function$
BEGIN
  UPDATE
    {table}
  SET
{set_block}
  WHERE id = _id;
END;
$function$;'''.format( args_type = ", ".join( args_type_list ),
                       table = self.data.Name( ),
                       args = ", ".join( args_list ),
                       fields = ", ".join( fields_list ),
                       set_block = ",\n".join( set_block_list ),
                       type = self.data.getIdentifier().getType()
                       )
        self.data.sql_file.Write( body.splitlines( ) )
