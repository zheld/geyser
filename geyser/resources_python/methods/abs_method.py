#!/usr/bin/env python
# coding=utf-8


class AbstractMethod( object ):
    def __init__( self, data, name ):
        self.name = name
        self.data = data
        self.procedure = '{table}_{method}'.format( table = self.data.Name( ),
                                                    method = self.Name( ) )
        self.args = [ ]
        self.doc = ''

    def Name( self ):
        return self.name

    def getArgsNameList( self ):
        return [ arg.Name( ) for arg in self.args ]

    def getNative( self ):
        pass

    def getApi( self, api_creater ):
        api_creater.addAPIMethod( self.table.Name( ), self.Name( ), self.args, None )

    def getProxy( self, classitem ):
        service = self.table.getService( ).Name( )
        body = '''{doc}
yield dispatcher.invoke('{service}', '{procedure}', {args} )'''.format( doc = self.doc,
                                                                        service = service,
                                                                        procedure = self.procedure,
                                                                        args = (', '.join( self.getArgsNameList( ) )) if self.args else [ ] )
        methoditem = classitem.addClassMethod( self.Name( ), self.getArgsNameList( ) )
        methoditem.addBody( body )

    def setClientMethod( self, row_class ):
        pass

    def getSqlProcedure( self ):
        pass

    def Serialize( self ):
        procjson = { }
        procjson[ 'name' ] = self.procedure
        return procjson
