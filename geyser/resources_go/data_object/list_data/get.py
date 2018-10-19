#!/usr/bin/env python
# coding=utf-8
from resources_go.data_object.go_methods.abs_method import AbstractMethod
from resources_go.types import go_types


class GetListDataGoMethod( AbstractMethod ):
    def __init__( self, data ):
        super( GetListDataGoMethod, self ).__init__( data, 'Get' )

    def getNative( self ):

        if isinstance( self.data.value_type, str ):
            raise Exception(">>>>>")
        else:
            for field in self.data.value_type.getFields( ):
                name = field.Name( ).capitalize( )
                func = self.data.gofile.addFunction( "GetBy{}".format( name ) )

                func.addArgs( "{field} {type}".format( field = field.Name( ),
                                                       type = go_types.go_converter(field.getType())
                                                       ) )
                func.addResults( "res []*{value_type}".format( value_type = self.data.getValueType( ) ) )

                body = '''    for _, value := range {data}_list <@
        if value.{name} == {field} <@
            res = append(res, value)
        @>
    @>
    return res'''.format( data = self.data.value_type.Name( ),
                          name = name,
                          field = field.Name( ) )
                func.addBody( body )
