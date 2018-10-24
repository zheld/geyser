#!/usr/bin/env python
# coding=utf-8
from geyser.resources_go.data_object.data import GoDataObject
from geyser.resources_go.types import go_types
from .add import Add
from .get import Get
from .len import Len
from .list import List
from .change import Change
from .delete import Delete
from .remove import Remove
from .get_id_with_insert import GetIdWithInsert
from .get_id_from_cache import GetIdFromCache


class Datacenter( GoDataObject ):
    def __init__( self, name, type, parent=None, public=True,
                  cache=False,
                  dictionary=False ):
        super( Datacenter, self ).__init__( name, parent )
        self.value_type = type
        self.auto_load = False
        self.init_rows = [ ]
        if cache:
            self.functions = [
                Len,
                GetIdFromCache,
            ]
        elif dictionary:
            self.functions = [
                Len,
                GetIdWithInsert,
            ]
        else:
            self.functions = [
                Add,
                Change,
                Remove,
                Delete,
                Len,
                Get,
                List
            ]
        self.indexes = [ ]

    def existDel( self ):
        '''есть ли в реестре методов есть удаления'''
        return Remove in self.functions

    def setAutoLoad( self ):
        # init
        self.init_rows.append( "    load()" )
        self.auto_load = True

    def addIndex( self, field ):
        self.indexes.append( field )

    def getIndexes( self ):
        return self.indexes

    def createGoType( self ):
        pass

    def BuildCustom( self ):
        # imports
        self.gofile.addImport( "sort" )
        self.gofile.addImport( self.value_type.getImport() )

        # main index
        idfield = self.value_type.getIdentifier()
        if idfield:
            self.indexes = [ idfield ] + [ fl for fl in self.indexes if fl != idfield ]
        elif not self.indexes:
            raise Exception( "Обязательно надо задать хотя бы один индекс для хранения данных" )

        # init
        if self.init_rows:
            func_init = self.gofile.addFunction( "init" )
            body = "\n".join( self.init_rows )
            func_init.addBody( body )

        # auto load
        if self.auto_load:
            self.AutoLoad()

        # all sort
        func_sort = self.gofile.addFunction( "to_sort" )

        if self.existDel():
            # delete id from all indexes
            func_del_all = self.gofile.addFunction( "from_indexes_del" )
            func_del_all.addArgs( "id {type}".format( type = self.value_type.getIdentifier().getGoType() ) )
            func_del_list = [ ]

        body_list = [ ]

        # indexes
        for not_main, index in enumerate( self.getIndexes() ):
            index_name = "index_{}".format( index.Name() )
            self.addVarSlice( index_name, self.value_type, True if not_main else False )

            # sort_field function
            fu_name = "to_sort_{field}".format( field = index.Name().capitalize() )
            fu = self.gofile.addFunction( fu_name )
            body = '''    sort.Slice({index_name}, func(i, j int) bool <@
    return {index_name}[i].{field} < {index_name}[j].{field}
    @>)'''.format( index_name = index_name,
                   field = index.Name().capitalize() )
            fu.addBody( body )
            body_list.append( "    {}()".format( fu_name ) )

            if self.existDel():
                # del o_sequence from index
                fu_del_name = "from_index_{}_del".format( index.Name() )
                fu_del = self.gofile.addFunction( fu_del_name )
                fu_del.addArgs( "id {type}".format( type = self.value_type.getIdentifier().getGoType() ) )
                body = '''    for position, element := range {index} <@
            if element.Id == id <@
                {index} = append({index}[:position], {index}[position + 1:]...)
                {sort_name}()
                break
            @>
        @>'''.format( index = index_name,
                      sort_name = fu_name )
                fu_del.addBody( body )
                func_del_list.append( "    go {}(id)".format( fu_del_name ) )

        func_sort.addBody( "\n".join( body_list ) )
        if self.existDel():
            func_del_all.addBody( "\n".join( func_del_list ) )

        # functions native
        for method_class in self.getMethods():
            method_class( self ).getNative()

            # self.BuildDataItem( )

    def getValueType( self ):
        return self.value_type.getFullType() if not isinstance( self.value_type, str ) else go_types.go_converter(self.value_type)

    def AutoLoad( self ):
        # load
        self.gofile.addImport( "core" )
        self.gofile.addImport( "fmt" )
        func = self.gofile.addFunction( "load" )
        func.addResults( "error" )
        indexes = "\n".join( "            index_{name} = append(index_{name}, {item})".format( name = fl.Name(),
                                                                                               item = "&(index_id[len(index_id) - 1])" if not_main else "item" )
                             for not_main, fl in enumerate( self.indexes ) )
        if self.value_type.getIdentifier().getGoType() != "string":
            body = '''    part_len := 1000
    last := 0
    for <@
        item_list, count, err := {package}.ListFilter(&last, part_len, nil)
        if err != nil <@
            core.PublishError("{datacenter}.load(): fail get part query: " + err.Error())
            return err
        @>
        for _, item := range item_list <@
{indexes}
        @>
        if part_len > count <@
            break
        @>
    @>
    to_sort()
    core.PublishInfo(fmt.Sprintf("{datacenter}.Load(): OK, len cache: [%v]", Len()))
    return nil'''.format( package = self.value_type.Name(),
                          datacenter = self.Name(),
                          indexes = indexes
                          )
        else:
            body = '''    item_list, err := {package}.List( )
    if err != nil <@
        core.PublishError("{datacenter}.load(): fail get part query: " + err.Error())
        return err
    @>
{indexes}
    to_sort()
    core.PublishInfo(fmt.Sprintf("{datacenter}.Load(): OK, len cache: [%v]", Len()))
    return nil'''.format( package = self.value_type.Name(),
                          datacenter = self.Name(),
                          indexes = indexes
                          )
        func.addBody( body )
