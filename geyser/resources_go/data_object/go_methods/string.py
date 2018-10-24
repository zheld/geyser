#!/usr/bin/env python
# coding=utf-8
from geyser.resources_python.methods.abs_method import AbstractMethod


class StringGoMethod( AbstractMethod ):
    def __init__( self, data ):
        super( StringGoMethod, self ).__init__( data, 'String' )
        self.args = [ ]

    def getNative( self ):
        self.data.gofile.addImport( "fmt" )
        func = self.data.gotype.addMethod( "String" )
        func.addResults( "str string" )

        fls = [ ]
        for field in self.data.getFields( ):
            fltmp = "{fl_name}: %v".format( fl_name = field.Name( ).capitalize( ) )
            fls.append( fltmp )

        body = '''    str = fmt.Sprintf("type: {gotype} [ {fields} ]", {var_fields})
    return'''.format( gotype = self.data.typeName,
                      fields = ', '.join( fls ),
                      var_fields = ', '.join( "self." + fl.Name( ).capitalize( ) for fl in self.data.getFields( ) )
                      )
        func.addBody( body )


