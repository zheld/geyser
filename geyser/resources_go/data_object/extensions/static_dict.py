#!/usr/bin/env python
# coding=utf-8
from geyser.item import Item
from geyser.resources_go.types import go_types


class StaticDict( Item ):
    def __init__( self, data, name, seq, default="" ):
        super( StaticDict, self ).__init__( name, data )
        self.seq = seq
        self.default = default

    def getNative( self, go_compiler ):
        return
        gofile = go_compiler.srv_api_package.addGoFile( "{service}.{module}.dict".format( service = go_compiler.service.Name(),
                                                                                          module = self.parent.Name().lower() ) )
        self.parent.extensions_file = gofile

        list_name = "{}_list".format( self.Name() )

        seq_list = [ ]
        for i in self.seq:
            seq_list.append( '"{}"'.format( i ) )
        value = "[]string<@{}@>".format( ", ".join( seq_list ) )

        gofile.addVar(list_name, value, go_types.text_array)

        # get_id
        func_get_id = gofile.addFunction( "Get{}{}Id".format( self.parent.Name().capitalize(),
                                                              self.Name().capitalize() ) )
        func_get_id.addArgs( "name string" )
        func_get_id.addResults( "int" )
        body_id = '''    for id, stname := range {list_name} <@
        if stname == name <@
            return id
        @>
    @>
    return -1'''.format( list_name = list_name )
        func_get_id.addBody( body_id )

        # get_name
        func_get_name = gofile.addFunction( "Get{}{}Name".format( self.parent.Name().capitalize(),
                                                                  self.Name().capitalize() ) )
        func_get_name.addArgs( "id int" )
        func_get_name.addResults( "string" )
        body_name = '''    if id < 0 <@
        return "{default}"
    @>
    if id < len({list_name}) <@
    return {list_name}[id]
    @>
    return ""'''.format( list_name = list_name,
                         default = self.default )
        func_get_name.addBody( body_name )
