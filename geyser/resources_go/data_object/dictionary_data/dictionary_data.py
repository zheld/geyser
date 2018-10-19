#!/usr/bin/env python
# coding=utf-8
from resources_go.data_object.data import GoDataObject
from resources_go.types import go_types
from .add import AddDictionaryDataGoMethod
from .get import GetDictionaryDataGoMethod
from .len import LenDictionaryDataGoMethod
from .remove import RemoveDictionaryDataGoMethod


class GoDictionaryData( GoDataObject ):
    def __init__( self, name, key, value, parent=None, public=True ):
        super( GoDictionaryData, self ).__init__( name, parent )
        self.key_type = key
        self.value_type = value
        self.value_type_name = go_types.go_converter(value) if isinstance(value, str) else value.Name()
        self.functions = [ AddDictionaryDataGoMethod,
                           GetDictionaryDataGoMethod,
                           RemoveDictionaryDataGoMethod,
                           LenDictionaryDataGoMethod,

        ]

    def createGoType( self ):
        pass

    def BuildCustom( self ):
        self.addVarMap( "{}_map".format( self.Name() ), self.key_type, self.value_type )
        # functions native
        for method_class in self.getMethods( ):
            method_class( self ).getNative( )

    def getKeyType( self ):
        return "{}.{}".format(self.key_type.Name(), self.key_type.getType()) if not isinstance( self.key_type, str ) else go_types.go_converter(self.key_type)

    def getValueType( self ):
        return "{}.{}".format(self.value_type.Name(), self.value_type.getType()) if not isinstance( self.value_type, str ) else go_types.go_converter(self.value_type)
