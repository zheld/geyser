#!/usr/bin/env python
# coding=utf-8
from methods.delete import Delete
from methods.list import List

from generator.Python.pyfile import PyFile
from geyser.resources_python.methods.update import Update

imp = '''from core import *
from bl.m_crumbs.crumbs_list import CrumbsList
from core.info_page.abstract_info_page import InfoPage
from core.info_page.info_row_block.info_row_block import RowBlock
from core.list.manager import PageList'''


class TableModule:
    def __init__( self, table ):
        self.table = table
        self.row_class = self.table.Name( ).capitalize( )
        self.list_class = self.row_class + 'List'


    def ModuleCode( self, pyfile ):
        pyfile.AddImport( imp )

        # InfoPage subclass
        row_class = pyfile.AddClassItem( self.row_class, 'InfoPage' )

        # add single
        row_class.addStaticField( 'single', True )

        # __init__
        method_init = row_class.addMethod( '__init__', [ '_id', 'parent=None' ] )
        method_init.Write( self.Get__init__Body( ) )


        for method in self.table.getMethods( ):
            method(self.table).setClientMethod(row_class)



        # delete
        method_delete = row_class.addMethod( 'delete', [ '_id' ] )
        method_delete.Write( self.GetOtherBody( Delete ) )

        # list
        method_list = row_class.addClassMethod( 'list', [ ] )
        method_list.Write( self.GetOtherBody( List ) )

        # update
        method_update = row_class.addMethod( 'update', [ ] )
        method_update.Write( self.GetUpdateBody( ) )

        # PageList subclass
        list_class = pyfile.AddClassItem( self.list_class, 'PageList' )

        # __init__
        list_init = list_class.addMethod( '__init__', [ 'parent=None' ] )
        list_init.Write( self.GetPageListInit( ) )


    def Save( self, path=None ):
        pyfile = PyFile( 'm_' + self.table.Name( ) )
        self.ModuleCode( pyfile )
        pyfile.Save( path )


    def GetPageListInit( self ):
        return '''super({listclass}, self).__init__(parent)
self.setTitle('{listclass}')
self.setInfoClass({rowclass})
self.build_list()
CrumbsList.add('{listclass}', self)'''.format( listclass = self.list_class,
                                                rowclass = self.row_class )


    def GetUpdateBody( self ):
        modif_field_list = self.table.getModifiedFields( )
        field_block = [ ]
        for field in modif_field_list:
            field_block.append( "{name} = info['{name}']".format( name = field.Name( ) ) )
        field_block = '\n'.join( field_block )
        field_list = ', '.join( fld.Name( ) for fld in modif_field_list )

        body = '''
info = self.compile_edit_info()
{field_block}
try:
    get_service('{service}').{procedure}(packer(self.id, {field_list})).get()
except ChokeEvent:
    return True'''.format( field_block = field_block,
                           service = self.table.getService( ).Name( ),
                           procedure = Update( self.table ).procedure,
                           field_list = field_list )

        return body


    def GetOtherBody( self, methodclass ):
        body = '''res = get_service('{servicename}').{procedure}(packer()).get()
return unpacker(res)'''.format( servicename = self.table.getService( ).Name( ),
                                procedure = methodclass( self.table ).procedure )
        return body


    def Get__init__Body( self ):
        row_block_items = [ ]
        for idx, field in enumerate( self.table.getFields( ) ):
            row_block_item = "row_block.add_row('{name}', _info[{idx}], {modified})".format( name = field.Name( ),
                                                                                             idx = idx,
                                                                                             modified = not field.isConst( ) )
            row_block_items.append( row_block_item )
        row_block_items = '\n'.join( row_block_items )

        body = '''super({rowclass}, self).__init__(parent)
self.id = _id

_info = {rowclass}.read(self.id)

self.set_title('{rowclass}')

# info observer
row_block = RowBlock(self)
{row_block_items}
self.add_block(row_block)

CrumbsList.add('{rowclass}: ' + self.name, self)
        '''.format( rowclass = self.row_class,
                    row_block_items = row_block_items )
        return body
