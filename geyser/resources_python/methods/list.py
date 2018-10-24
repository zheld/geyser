#!/usr/bin/env python
# coding=utf-8
from geyser.resources_python.methods.abs_method import AbstractMethod


class List( AbstractMethod ):
    def __init__( self, table ):
        super( List, self ).__init__( table, 'List' )
        self.args = [ table.getIdentifier( ) ]

    def getNative( self, classitem ):
        body = '''filter_list = []
filter_block = ''

if _filter:
    filter_list.append( '{} = {}'.format( name, value ) for name, value in _filter.items( ) )
if _from:
    filter_list.append( '%s > {}'.format(_from))
if filter_list:
    filter_block = 'WHERE ' + ' AND '.join(filter_list)

yield sql_async_all( "SELECT * FROM %s {} LIMIT %s".format(filter_block) )
        ''' % (self.table.getIdentifier( ).Name( ), self.table.Name( ), '100')

        methoditem = classitem.addClassMethod(self.Name(), ['_filter', '_from'])
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
