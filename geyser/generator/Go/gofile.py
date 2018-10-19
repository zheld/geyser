#!/usr/bin/env python
# coding=utf-8
from generator.FSItem.file import File
from generator.Go.goitem import *


class GoFile( File ):
    def __init__( self, name, package=None, package_name=None, only_create=False ):
        super( GoFile, self ).__init__( name + '.go', package, only_create )
        self.import_block = GoImport( self )
        self.addItem( self.import_block )
        self.var_list = GoVarList( self )
        self.addItem( self.var_list )
        self.body = [ 'package {}\n'.format( package_name or (self.parent.Name( ) if self.parent else None) or 'main' ) ]

    def addFunction( self, name ):
        foo = GoFunctionSimple( name, self )
        self.addItem( foo )
        return foo

    def addType( self, name, core="struct" ):
        gt = GoType( name, self, core )
        self.addItem( gt )
        return gt

    def addVar( self, name, value=None, type=None, const=False ):
        var = GoVar( name, self, value, const )
        if type:
            var.addType( type )
        self.var_list.addGoVar( var )
        return var

    def addImport( self, imp ):
        self.import_block.addImport( imp )
