from geyser.item import Item


class GeneratorItem( Item ):
    # File System item

    def __init__( self, name, parent=None ):
        super( GeneratorItem, self ).__init__( name, parent )

    def Build( self ):
        pass

