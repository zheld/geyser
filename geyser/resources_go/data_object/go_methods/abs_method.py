#!/usr/bin/env python
# coding=utf-8


class AbstractMethod( object ):
    def __init__( self, data, name ):
        self.name = name
        self.data = data
        self.procedure = '{table}_{method}'.format( table = self.data.Name( ),
                                                    method = self.Name( ).lower() )
        self.args = [ ]
        self.doc = ''

    def Name( self ):
        return self.name

    def getArgsNameList( self ):
        return [ arg.Name( ) for arg in self.args ]

    def getNative( self ):
        pass

    def getSqlProcedure( self ):
        pass

    def Serialize( self ):
        # method to serialize method for saving database structure during conversion
        procjson = { }
        procjson[ 'name' ] = self.procedure
        return procjson
