#!/usr/bin/env python
# coding=utf-8
from resources_python.methods.abs_method import AbstractMethod


class Custom( AbstractMethod ):
    def __init__( self, cls, name, doc, *args ):
        super( Custom, self ).__init__( cls, 'Read' )

    def getNative( self ):
        body = '''yield sql_async_one('SELECT {procedure}(' + str({pkey}) + ')')'''.format( procedure = self.procedure,
                                                                                            pkey = self.table.getIdentifier( ) )

    def getSqlProcedure( self ):
        fields = ', '.join( '{}.{}'.format( self.table.Name(), fl.Name() ) for fl in self.table.getFields( ) )
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
                       table = self.table.Name(),
                       pkey = self.table.getIdentifier( ).Name( )
                       )
        return body
