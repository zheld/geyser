#!/usr/bin/env python
# coding=utf-8
from item import Item


class PyItem( Item ):
    def __init__( self, name, parent=None ):
        super( PyItem, self ).__init__( name, parent )
        self.ident = parent.ident + 1 if parent else 0
        self.header_rows = [ ]

    def Header( self ):
        header = [ ]
        for row in self.header_rows:
            header.append( RowItem( row, self.parent ) )
        return header

    def Build( self ):
        result = [ ]
        rows = self.Header( )
        self.items = rows + self.items
        for item in self.getList( ):
            result += item.Build( )
        return result


class ClassItem( PyItem ):
    def __init__( self, name, parent=None, classparent=None ):
        super( ClassItem, self ).__init__( name, parent )
        self.classparent = '({})'.format( classparent ) if classparent else ''
        self.header_rows = [ 'class {}{}:'.format( self.Name( ), self.classparent ) ]

    def addClass( self, name, classparent=None ):
        # Добавить подкласс
        cls = ClassItem( name, self, classparent )
        self.addItem( cls )
        return cls

    def addMethod( self, name, args ):
        # Довавить метод в класс
        method = MethodItem( name, args, False, self )
        self.addItem( method )
        return method

    def addClassMethod( self, name, args ):
        # Добавить статический метод класса
        method = MethodItem( name, args, True, self )
        self.addItem( method )
        return method

    def addStaticField( self, name, value ):
        # Добавить переменную класса
        field = RowItem( '{} = {}'.format( name, value ), self )
        self.addItem( field )
        return field


class MethodItem( PyItem ):
    def __init__( self, name, args, classmethod, parent=None ):
        super( MethodItem, self ).__init__( name, parent )
        self.first_arg = [ 'cls' ] if classmethod else [ 'self' ]
        self.args = self.first_arg + args
        self.classmethod = classmethod
        self.header_rows = [ '@classmethod' ] if self.classmethod else [ ]
        self.header_rows.append( 'def {}({}):'.format( self.Name( ),
                                                       ', '.join( self.args ) ) )
        self.split_item = ''

    def addBody( self, code ):
        if isinstance( code, str ):
            code = code.splitlines( )
        for row in code:
            row_item = RowItem( row, self )
            self.addItem( row_item )
        self.addItem( RowItem( '\n', self ) )


class FunctionItem( PyItem ):
    def __init__( self, name, args, decorators=[ ], parent=None ):
        super( FunctionItem, self ).__init__( name, parent )
        self.args = args
        self.header_rows = decorators
        self.header_rows.append( 'def {}({}):'.format( self.Name( ),
                                                       ', '.join( self.args ) ) )
        self.split_item = ''

    def addBody( self, code ):
        if isinstance( code, str ):
            code = code.splitlines( )
        for row in code:
            row_item = RowItem( row, self )
            self.addItem( row_item )
        self.addItem( RowItem( '\n', self ) )


class RowBlockItem( PyItem ):
    def __init__( self ):
        super( RowBlockItem, self ).__init__( None )

    def addRows( self, imp ):
        self.addItem( imp )

    def Build( self ):
        return self.getList( )


class RowItem( PyItem ):
    def __init__( self, text, parent=None ):
        super( RowItem, self ).__init__( None, parent )
        self.text = text
        self.tab = 4

    def Build( self ):
        return [ ' ' * self.tab * self.ident + self.text ]
