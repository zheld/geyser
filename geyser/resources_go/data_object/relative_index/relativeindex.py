#!/usr/bin/env python
# coding=utf-8
from resources_go.data_object.data import GoDataObject
from resources_go.data_object.datacenter.datacenter import Datacenter
from resources_go.types import go_types


class RelativeIndex( GoDataObject ):
    def __init__( self, data, foreign_type, parent=None ):
        super( RelativeIndex, self ).__init__( "loader_" + data.Name( ), parent )
        self.data = data
        self.foreign_type = foreign_type
        self.init_rows = [ ]

        # relation structure
        self.data.hasGetId( )
        self.reldata = GoDataObject( "relation_" + data.Name( ), self )
        self.inside_data_list.append( self.reldata )
        if self.reldata:
            # fields
            self.foreign_id = self.reldata.addIdentifierNoAuto( self.foreign_type )
            self.local_id = self.reldata.addField( "localid", go_types.integer)
            # table
            self.index_table = self.reldata.addTable( )
            # properties
            self.reldata.addSignatureRowIndex( self.foreign_id, self.local_id )
            if self.index_table:
                self.index_table.addUniqueIndex( self.foreign_id, self.local_id )

        # index datacenter
        self.datacenter = Datacenter( "index_" + data.Name( ), self.reldata, self )
        self.inside_data_list.append( self.datacenter )
        if self.datacenter:
            self.datacenter.setAutoLoad( )

    def BuildCustom( self ):
        self.gofile.addImport( "core" )
        self.gofile.addImport( self.datacenter.getImport( ) )
        self.funcGet( )

    def funcGet( self ):
        func = self.gofile.addFunction( "Get{data}Id".format( data = self.data.Name( ).capitalize( ) ) )

        func_args_list = [ ]
        invoke_args_list = [ ]

        for field in self.data.getFields( ):
            if not field.isAuto( ):
                func_args_list.append( "{name} {type}".format(name = field.Name( ),
                                                              type = go_types.go_converter(field.getType())))
                invoke_args_list.append( field.Name( ) )

        invoke_args = ", ".join( invoke_args_list )
        func_args = ", ".join( func_args_list )

        func.addArgs( "foreign {foreign_type}, {func_args}".format(data = self.data.Name( ),
                                                                   func_args = func_args,
                                                                   foreign_type = go_types.go_converter(self.foreign_type)))
        func.addResults( "int, error" )

        body = '''    {data}_id_list, count := index_{data}.GetById(foreign)
    if count == 0 <@
        res_interface, err := core.Invoke("{service}", "get_{data}_id", {invoke_args})
        if err != nil <@
            return 0, err
        @>
        localid := core.ToInt(res_interface)
        _, err = index_{data}.Add(foreign, localid)
        if err != nil <@
            return localid, err
        @>
        return localid, nil
    @>
    return {data}_id_list[0].Localid, nil'''.format( data = self.data.Name( ),
                                                     invoke_args = invoke_args,
                                                     service = self.data.getService( ).Name( ) )
        func.addBody( body )
