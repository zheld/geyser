#!/usr/bin/env python
# coding=utf-8
from geyser.resources_python.methods.abs_method import AbstractMethod


class Delete(AbstractMethod):
    def __init__(self, table):
        super(Delete, self).__init__(table, 'Delete')
        self.args = [ table.getIdentifier( ) ]

    def getNative(self, classitem):
        body = '''yield sql_async_one('SELECT {procedure}(' + str({pkey}) + ')')'''.format( procedure = self.procedure,
                                                                                            pkey = self.table.getIdentifier( ).Name( ) )
        methoditem = classitem.addClassMethod(self.Name(), self.getArgsNameList())
        methoditem.addBody( body )

    def getSqlProcedure( self ):
        body = '''
CREATE OR REPLACE FUNCTION public.{procedure}( _id {pkey_type} )
    RETURNS VOID
    LANGUAGE plpgsql
AS $function$
BEGIN
    DELETE
    FROM
        {table}
    WHERE
        {pkey} = _id;
END;
$function$;'''.format( procedure = self.procedure,
                       pkey_type = self.table.getIdentifier( ).getType( ),
                       table = self.table.Name(),
                       pkey = self.table.getIdentifier( ).Name( )
                       )
        return body
