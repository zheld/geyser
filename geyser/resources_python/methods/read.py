#!/usr/bin/env python
# coding=utf-8
from resources_python.methods.abs_method import AbstractMethod


class Read( AbstractMethod ):
    def __init__( self, table ):
        super( Read, self ).__init__( table, 'Read' )
        self.args = [ table.getIdentifier( ) ]

    def getNative( self, classitem ):
        body = '''yield sql_async_one('SELECT {procedure}(' + str({pkey}) + ')')'''.format( procedure = self.procedure,
                                                                                            pkey = self.table.getIdentifier( ).Name( ) )
        methoditem = classitem.addClassMethod(self.Name(), self.getArgsNameList())
        methoditem.addBody( body )

    def getSqlProcedure( self ):
        fields = ', '.join( '{}.{}'.format( self.table.Name( ), fl.Name( ) ) for fl in self.table.getFields( ) )
        body = '''
CREATE OR REPLACE FUNCTION public.{procedure}( _id {pkey_type} )
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
        {pkey} = _id INTO result;
  RETURN result;
END;
$function$;'''.format( procedure = self.procedure,
                       pkey_type = self.table.getIdentifier( ).type,
                       fields = fields,
                       table = self.table.Name( ),
                       pkey = self.table.getIdentifier( ).Name( )
                       )
        return body


    def setClientMethod( self, row_class ):
        # read
        method_read = row_class.addClassMethod( 'read', self.getArgsNameList( ) )

        body = '''res = get_service('{servicename}').{procedure}(packer({args})).get()
return unpacker(res)'''.format( servicename = self.table.getService( ).Name( ),
                                procedure = self.procedure,
                                args = ', '.join(self.getArgsNameList()) )

        method_read.Write( body )
        return body
