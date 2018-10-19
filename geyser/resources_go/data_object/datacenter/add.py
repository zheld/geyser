#!/usr/bin/env python
# coding=utf-8
from resources_go.data_object.go_methods.abs_method import AbstractMethod


class Add( AbstractMethod ):
    def __init__( self, data ):
        super( Add, self ).__init__( data, 'Add' )

    def getNative( self ):
        func = self.data.gofile.addFunction( self.Name() )

        method_args_list = [ ]
        vars_list = [ ]
        for field in self.data.value_type.getFields():
            if not field.isAuto():
                method_args_list.append( "{name} {type}".format( name = field.Name(), type = field.getGoType() ) )
                vars_list.append( field.Name() )

        method_args = ", ".join( method_args_list )
        vars = ", ".join( vars_list )

        func.addResults( "res {type}, err error".format( type = self.data.value_type.getIdentifier().getGoType() ) )
        func.addArgs( method_args )

        add_body_list = [ ]
        for number, index in enumerate( self.data.getIndexes() ):
            add_body_list.append( '''        index_{index} = append(index_{index}, {newitem})'''.format( index = index.Name(),
                                                                                                                newitem = "&(index_id[len(index_id) - 1])" if number != 0 else "newitem" ) )

        if self.data.value_type.getIdentifier().isAuto():
            body = '''    newitem, err := {package}.InsertReadReturnInstance({vars})
    if err != nil <@
        return 0, err
    @>
    _, count := GetById(newitem.Id)
    if count == 0 <@
{app_list}
        to_sort()
    @>
    return newitem.Id, nil'''.format( package = self.data.value_type.Name(),
                                      vars = vars,
                                      app_list = "\n".join( add_body_list )
                                      )
        else:
            body = '''    newitem, err := {package}.InsertReturnInstance({vars})
    if err != nil <@
        return res, err
    @>
{app_list}
    to_sort()
    return newitem.Id, nil'''.format( package = self.data.value_type.Name(),
                                      vars = vars,
                                      app_list = "\n".join( add_body_list ),
                                      )

        func.addBody( body )
