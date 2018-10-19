from generator.FSItem.file import File


class JsonFile( File ):
    def __init__( self, name, parent=None, only_create=False ):
        super( JsonFile, self ).__init__( name + '.json', parent, only_create = only_create )
