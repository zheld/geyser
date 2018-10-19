#!/usr/bin/env python
# coding=utf-8
from resources_python.methods.abs_method import AbstractMethod


class Update( AbstractMethod ):
    def __init__( self, table ):
        super( Update, self ).__init__( table, 'Update' )
        self.args = [ table.getIdentifier( ) ] + self.table.getModifiedFields( )


    def getNative( self, classitem ):
        body = '''yield sql_async_one('SELECT {procedure}(' + str({pkey}) + ')')'''.format( procedure = self.procedure,
                                                                                            pkey = self.table.getIdentifier( ).Name( ) )
        methoditem = classitem.addClassMethod(self.Name(), self.getArgsNameList())
        methoditem.Write( body )


    def getSqlProcedure( self ):
        body = ''
        return body
