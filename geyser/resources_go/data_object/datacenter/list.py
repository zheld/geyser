#!/usr/bin/env python
# coding=utf-8
from resources_go.data_object.go_methods.abs_method import AbstractMethod


class List( AbstractMethod ):
    def __init__( self, data ):
        super( List, self ).__init__( data, 'List' )

    def getNative( self ):
        func = self.data.gofile.addFunction( self.Name( ) )
        self.data.gofile.addImport("strconv")
        func.addArgs("page int")
        func.addResults( "[]{value_type}".format( value_type = self.data.getValueType( ) ) )
        body = '''    if page < 0 <@
        return index_{field}
    @>
    rec_on_page, err := strconv.Atoi(core.GetSetting("rec_on_page", "50"))
    if err != nil <@
        rec_on_page = 50
    @>
    rec_from := page * rec_on_page
    return index_{field}[rec_from: rec_from + rec_on_page]'''.format( field = self.data.indexes[ 0 ].Name( ) )
        func.addBody( body )
