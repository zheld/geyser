from generator.Json.jsonfile import JsonFile
import json
import datetime


class ManifestFile( JsonFile ):
    def __init__( self, service, parent ):
        super( ManifestFile, self ).__init__( 'manifest', parent )
        self.service = service

        # work with the manifest file, if there is no file - just create a balloon, if it exists
        # Parse it, edit the data and write it back
        builded = str( datetime.datetime.now( ) )
        try:
            manifest = json.loads( self.Read( ) )
            version = manifest[ 'version' ]

            # if the current version of the service is different from the version of the new service, then we start
            # the build number from zero, if not - just increment the counter
            if version == self.service.version:
                manifest[ 'build' ] += 1
            else:
                manifest[ 'build' ] = 1
                manifest[ 'version' ] = self.service.version
            manifest['last_build'] = builded
            self.body.append( json.dumps( manifest, separators = (',\n', ': ') ) )
        except Exception as e:
            manifest_obj = {
                "slave": "{service}".format( service = self.service.Name( ) ),
                "name": "{service}".format( service = self.service.Name( ) ),
                "version": "0.1",
                "build": 1,
                'created': builded,
                'last_build': builded }
            self.body.append( json.dumps( manifest_obj ) )
