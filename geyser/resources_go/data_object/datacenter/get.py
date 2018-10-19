#!/usr/bin/env python
# coding=utf-8
from resources_go.data_object.go_methods.abs_method import AbstractMethod
from resources_go.types import go_types


class Get( AbstractMethod ):
    def __init__( self, data ):
        super( Get, self ).__init__( data, 'GetBy' )

    def getNative( self ):

        if isinstance( self.data.value_type, str ):
            raise Exception(">>>>>")
        else:
            for field in self.data.value_type.getFields():
                name = field.Name().capitalize()
                func = self.data.gofile.addFunction( "GetBy{}".format( name ) )

                if field not in self.data.getIndexes():

                    func.addArgs( "{field} {type}".format( field = field.Name(),
                                                           type = go_types.go_converter(field.getType())
                                                           ) )
                    func.addResults( "res []*{value_type}, count int".format( value_type = self.data.getValueType() ) )

                    body = '''    for idx, value := range index_{first_index} <@
        if value.{name} == {field} <@
            res = append(res, &(index_{first_index}[idx]))
            count++
        @>
    @>
    return res, count'''.format( name = name,
                                 field = field.Name(),
                                 first_index = self.data.getIndexes()[ 0 ].Name() )
                else:
                    func.addArgs( "{field} {type}".format( field = field.Name(),
                                                           type = go_types.go_converter(field.getType())
                                                           ) )
                    func.addResults( "res []*{value_type}, count int".format( value_type = self.data.getValueType() ) )
                    value = "index_{field}[res_idx]".format( field = field.Name() )
                    if field == self.data.getIndexes()[ 0 ]:
                        value = "&({value})".format( value = value )
                    body = '''    res_idx := sort.Search(Len(), func(i int) bool <@
        return index_{field}[i].{name} >= {field}
    @>)

    INTO_RES:
    if res_idx < Len() <@
        count++
        value := {value}
        if value.{name} == {field} <@
            res = append(res, value)
            res_idx++
            goto INTO_RES
        @>
    @>
    return res, count'''.format( field = field.Name(),
                                 name = name,
                                 data = self.data.Name(),
                                 value = value
                                 )
                func.addBody( body )
