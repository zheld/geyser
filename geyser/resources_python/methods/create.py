#!/usr/bin/env python
# coding=utf-8
from geyser.resources_python.methods.abs_method import AbstractMethod


class Create( AbstractMethod ):
    def __init__( self, table ):
        super( Create, self ).__init__( table, 'Create' )
        self.args = [ fl for fl in table.getFields( ) if not fl.isAuto( ) and not fl.isIdentifier( ) ]

    def getNative( self, classitem ):
        args = " + ', ' + ".join(fl.getNameQuotes() for fl in self.args)
        body = '''yield sql_async_scalar( "SELECT {procedure}( " + {args} + " )" )'''.format( procedure = self.procedure,
                                                                                              args = args )
        methoditem = classitem.addClassMethod(self.Name(), self.getArgsNameList())
        methoditem.addBody( body )

    def getSqlProcedure( self ):
        args = ', '.join( 'p_' + fl.Name( ) for fl in self.args )
        fields = ', '.join( fl.Name( ) for fl in self.args )
        args_type = ', '.join( 'p_{} {}'.format( fl.Name( ), fl.type ) for fl in self.args )
        body = '''
CREATE OR REPLACE FUNCTION public.{procedure}( {args_type} )
    RETURNS INTEGER
    LANGUAGE plpgsql
AS $function$
DECLARE
  result INTEGER;
BEGIN
  INSERT INTO {table} ({fields})
      VALUES ({args}) RETURNING {table}_id INTO result;
  RETURN result;
END;
$function$;'''.format( procedure = self.procedure,
                       args_type = args_type,
                       table = self.table.Name( ),
                       args = args,
                       fields = fields
                       )
        return body

    def setClientMethod( self, row_class ):
        # new
        method_new = row_class.addClassMethod( 'new', [ 'name' ] )
        method_new.Write( self.GetOtherBody( Create ) )

    def setClientMethod( self, row_class ):
        # read
        method_read = row_class.addClassMethod( 'new', self.getArgsNameList( ) )

        body = '''res = get_service('{servicename}').{procedure}(packer({args})).get()
return unpacker(res)'''.format( servicename = self.table.getService( ).Name( ),
                                procedure = self.procedure,
                                args = ', '.join(self.getArgsNameList()) )

        method_read.Write( body )
        return body
