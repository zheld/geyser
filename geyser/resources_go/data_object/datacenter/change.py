#!/usr/bin/env python
# coding=utf-8
from geyser.resources_go.data_object.go_methods.abs_method import AbstractMethod
from geyser.resources_go.types import go_types


class Change( AbstractMethod ):
    def __init__( self, data ):
        super( Change, self ).__init__( data, 'Change' )

    def getNative( self ):
        self.data.gofile.addImport("core")
        for field in self.data.value_type.getFields():
            t = field.getType()
            if t == go_types.timestamp:
                self.data.gofile.addImport( "time" )

        func = self.data.gofile.addFunction( self.Name( ) )

        method_args_list = [ ]
        vars_list = [ ]
        for field in self.data.value_type.getFields( ):
            if not field.isAuto( ) and not field.isConst( ) and not field.isIdentifier( ):
                method_args_list.append( "{name} {type}".format( name = field.Name( ), type = field.getGoType( ) ) )
                vars_list.append( "    item.{ufield} = {field}".format( ufield = field.Name( ).capitalize( ),
                                                                        field = field.Name( ) ) )

        method_args = "id {type}, ".format( type = self.data.value_type.getIdentifier( ).getGoType( ) ) + ", ".join( method_args_list )
        vars = "\n".join( vars_list )

        func.addResults( "err error" )
        func.addArgs( method_args )

        add_body_list = [ ]
        for index in self.data.getIndexes( ):
            add_body_list.append( '''    index_{index} = append(index_{index}, newitem)'''.format( index = index.Name( ) ) )

        body = '''    item_list, count := GetById(id)
    if count == 0 <@
        msg := fmt.Sprintf("{data}: Change: not {value_type} with id = %v", id)
        core.PublishError(msg)
        return errors.New(msg)
    @>
    item := item_list[0]
    tmp_item := item

{vars}

    err = item.Update()
    if err != nil <@
        item = tmp_item
        return err
    @>
    to_sort()
    return nil'''.format( data = self.data.Name( ),
                          value_type = self.data.value_type.Name( ),
                          vars = vars )

        func.addBody( body )
