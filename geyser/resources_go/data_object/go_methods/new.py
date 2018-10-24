#!/usr/bin/env python
# coding=utf-8
from geyser.resources_python.methods.abs_method import AbstractMethod


class NewGoMethod( AbstractMethod ):
    def __init__( self, data ):
        super( NewGoMethod, self ).__init__( data, "New" )
        self.args = [ ]

    def getNative( self ):
        self.data.gofile.addImport( "fmt" )
        func = self.data.gofile.addFunction( self.Name() + self.data.gotype.Name( ) )
        func.addResults( "*" + self.data.gotype.Name( ) )

        body = '''    return &%s{} ''' % self.data.gotype.Name( )

        func.addBody( body )

