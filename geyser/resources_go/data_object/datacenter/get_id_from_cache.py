#!/usr/bin/env python
# coding=utf-8
from resources_go.data_object.go_methods.abs_method import AbstractMethod
from resources_go.types import go_types


class GetIdFromCache( AbstractMethod ):
    def __init__( self, data ):
        super( GetIdFromCache, self ).__init__( data, 'GetIdFromCache' )

    def getNative( self ):
        if not len( self.data.getIndexes() ) == 2:
            return
        if isinstance( self.data.value_type, str ):
            raise Exception(">>>>>")
        else:
            self.data.gofile.addImport( "core" )

            field = self.data.getIndexes()[ 1 ]
            func = self.data.gofile.addFunction( self.Name() )

            func.addArgs( "{field} {type}".format( field = field.Name(),
                                                   type = go_types.go_converter(field.getType())
                                                   ) )
            func.addResults( "int, error" )

            body = '''    res_idx := sort.Search(Len(), func(i int) bool <@
        return index_{field}[i].{name} >= {field}
    @>)

    if res_idx < Len() && index_{field}[res_idx].{name} == {field}<@
        value := index_{field}[res_idx]
        return value.Id, nil
    @> else <@
        core.PublishWarning("{data_name}_cache: GetIdFromCache: call cross cache")
        newitem, err := {data_name}.ReadByUnique({field})
        if err != nil <@
            return 0, err
        @>
        index_id = append(index_id, newitem)
        index_{field} = append(index_{field}, &(index_id[len(index_id) - 1]))
        to_sort()
        return newitem.Id, nil
    @>'''.format( name = field.Name().capitalize(),
                  field = field.Name(),
                  data_name = self.data.value_type.Name()
                  )

            func.addBody( body )
