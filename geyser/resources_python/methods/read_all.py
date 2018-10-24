#!/usr/bin/env python
# coding=utf-8
from geyser.resources_python.methods.abs_method import AbstractMethod


class ReadAll( AbstractMethod ):
    def __init__( self, table ):
        super( ReadAll, self ).__init__( table, 'ReadAll' )
        self.args = [ table.getIdentifier( ) ]

    def getNative( self, classitem ):
        methoditem = classitem.addClassMethod(self.Name(), self.getArgsNameList())
        if not self.table.CheckExistsRemoteForeign( ):
            body = '''yield sql_async_one('SELECT {procedure}(' + str({pkey}) + ')')'''.format( procedure = self.procedure,
                                                                                                pkey = self.table.getIdentifier( ).Name( ) )
            methoditem.addBody( body )
        else:
            body = [ ]
            body.append( '''res = yield sql_async_one('SELECT {procedure}(' + str({pkey}) + ')') '''.format( procedure = self.procedure,
                                                                                                             pkey = self.table.getIdentifier( ).Name( ) ) )
            for idx, field in enumerate( self.table.getFields( ) ):
                if field.isForeign() and field.isForeignRemote():
                    body.append( '''res[{idx}] = yield {service}.{table}.Read(res[{idx}])'''.format( idx = idx,
                                                                                                     service = field.getService( ).Name( ),
                                                                                                     table = field.getDataObject( ).Name( ) ) )
            body.append( 'yield res' )
            methoditem.addBody( body )

    def getSqlProcedure( self ):
        fields = [ '{}.{}'.format( self.table.Name( ), fl.Name( ) ) for fl in self.table.getFields( ) ]
        join_block = [ ]

        for field in self.table.getFields( ):
            if field.isForeign() and not field.isForeignRemote( ):
                fields += [ '{}.{}'.format( field.getDataObject( ).Name( ), fl.Name( ) ) for fl in field.getForeignFields( ) ]
                join_block.append( '''LEFT JOIN {join_table}
        ON {join_table}.{foreign} = {table}.{foreign}'''.format( join_table = field.field.getDataObject( ).Name( ),
                                                                 table = self.table.Name( ),
                                                                 foreign = field.Name( ) ) )
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
    {join_block}
    WHERE
        {table}.{pkey} = _id INTO result;
  RETURN result;
END;
$function$;'''.format( procedure = self.procedure,
                       pkey_type = self.table.getIdentifier( ).type,
                       fields = ', '.join( fields ),
                       table = self.table.Name( ),
                       join_block = '\n'.join( join_block ),
                       pkey = self.table.getIdentifier( ).Name( )
                       )
        return body
