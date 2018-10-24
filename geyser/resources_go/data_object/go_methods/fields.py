#!/usr/bin/env python
# coding=utf-8
from geyser.resources_go.data_object.go_methods.abs_method import AbstractMethod
from geyser.resources_go.types import go_types


class Fields( AbstractMethod ):
    def __init__( self, data ):
        super( Fields, self ).__init__( data, 'Fields' )

    def getNative( self ):
        if not self.data.table:
            return
        func = self.data.gotype.addMethod( self.Name() )
        func.addResults( "[]interface{}" )

        vars_list = [ ]
        for field in self.data.getFields():
            if field.getType() == go_types.timestamp:
                vars_list.append( '''    if self.{field}.IsZero() <@
        res = append(res, "")
    @> else <@
        res = append(res, self.{field}.String())
    @>'''.format( field = field.Name().capitalize() ) )
            else:
                field_upper = field.Name().capitalize() if not field.isData() else "{}.Id".format( field.Name().capitalize() )
                vars_list.append( "    res = append(res, self.{field_upper})".format( field_upper = field_upper ) )

        vars = "\n".join( vars_list )

        body = '''    res := []interface<@@><@@>
{vars}
    return res'''.format( vars = vars )
        func.addBody( body )
