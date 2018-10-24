from geyser.resources_go.data_object.data import GoDataObject
from geyser.resources_go.data_object.datacenter.datacenter import Datacenter
from geyser.resources_go.data_object.dictionary_data.dictionary_data import GoDictionaryData
from geyser.resources_go.data_object.static_data import GoStaticData
from geyser.resources_go.data_object.relative_index.relativeindex import RelativeIndex
from geyser.go_service_compiler import GoServiceCompiler
from geyser.item import Item
from geyser.resources_go.data_object.list_data.list_data import GoDataList
from geyser.resources_go.types import go_types


class ServiceBase( Item ):
    def __init__( self, name, version, config ):
        super( ServiceBase, self ).__init__( name )
        self.version = version

        data = GoDataObject( "history_conversions" )
        date = data.addAutoTimeStamp( "date" )
        build = data.addField( "build", go_types.text)
        structure = data.addField( "structure", go_types.text)
        self.history_table = data.addTable( )
        self.history_table.addUniqueIndex( date )
        self.srvconfig = config

    # data objects
    def addData( self, name, public=True ):
        if isinstance(name, str):
            do = GoDataObject( name, self, public )
        else:
            name.parent = self
            do = name
        self.addItem( do )
        return do

    # relative index
    def addRelativeIndex( self, data, foreign_type ):
        ri = RelativeIndex(data, foreign_type, self)
        self.addItem( ri )
        return ri

    # data static
    def addStaticData( self, name, public=True ):
        do = GoStaticData( name, self, public )
        self.addItem( do )
        return do

    # data dict
    def addDictionaryData( self, name, key, value, public=True ):
        data = GoDictionaryData( name, key, value, self, public )
        self.addItem( data )
        return data

    # data slice
    def addDataList( self, name, value, pointer=True, public=True ):
        data = GoDataList( name, value, self, pointer, public )
        self.addItem( data )
        return data

    # datacenter
    def addDataCenter( self, name, value, public=True, cache=False, dictionary=False ):
        data = Datacenter( name, value, self, public, cache = cache, dictionary=dictionary )
        self.addItem( data )
        return data

    def getDataList( self ):
        return self.getList( )

    def getData( self, name ):
        return self.Find( name )

    def getTables( self ):
        tables = [ self.history_table ]
        for data in self.getDataList( ):
            print(data.Name())
            tables += data.getTables()
        return tables

    def Generate(self):
        GoServiceCompiler(self).Build()

