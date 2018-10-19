#!/usr/bin/env python
# coding=utf-8
from generator.FSItem.file import File
from generator.Python.pyitem import ClassItem
from generator.Python.pyitem import RowBlockItem
from generator.Python.pyitem import FunctionItem


class PyFile( File ):
    def __init__( self, name, parent=None, only_create=False ):
        super( PyFile, self ).__init__( name + '.py', parent, only_create )
        self.import_block = RowBlockItem( )
        self.addItem( self.import_block )
        self.body = [ '# coding=utf-8' ]

    def addClass( self, name, base_class=None ):
        # Добавить класс в файл
        cls = ClassItem( name, classparent = base_class )
        self.addItem( cls )
        return cls

    def addFunction( self, name, args, decorators=[ ] ):
        # Добавить функцию
        foo = FunctionItem( name, args, decorators )
        self.addItem( foo )
        return foo

    def addImport( self, imp ):
        self.import_block.addRows( imp )

    def addRowsBlock( self, rows ):
        r = RowBlockItem( )
        r.addRows( rows )
        self.addItem( r )
        return r
