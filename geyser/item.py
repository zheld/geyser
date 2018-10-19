#!/usr/bin/env python
# coding=utf-8



class Item( object ):
    def __init__( self, name, parent=None ):
        self._name = name
        self.parent = parent
        self.items = [ ]

    def addItem( self, item ):
        self.items.append( item )

    def getList( self ):
        return self.items

    def Index( self, name ):
        for idx, item in enumerate( self.items ):
            try:
                itemname = item.Name( )
            except:
                itemname = item
            if itemname == name:
                return idx
        return None

    def Name( self ):
        return self._name

    def Find( self, name ):
        idx = self.Index( name )
        if idx is None:
            return None
        return self.items[ idx ]

    def __getattr__( self, name ):
        for item in self.items:
            if item.Name( ) == name:
                return item
        raise AttributeError( 'No attribute named {}'.format( name ) )

    def __getitem__( self, name ):
        for item in self.items:
            if item.Name( ) == name:
                return item
        raise AttributeError( 'No attribute named {}'.format( name ) )
