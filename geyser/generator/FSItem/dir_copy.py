#!/usr/bin/env python
# coding=utf-8
from geyser.generator.FSItem.fs_item import FSItem
from distutils.dir_util import copy_tree

class CopyDirectory(FSItem):
    def __init__( self, source, name, parent=None ):
        super(CopyDirectory, self).__init__(name, parent)
        self.source = source

    def Build( self ):
        try:
            source = self.source.getPath()
            dest = self.Name()
            print(source, " -> ", dest)
            copy_tree(source, dest)
        except OSError:
            pass
        except Exception as e:
            print('dir copy "{}" create is fail: {}'.format( self.Name(), e ))
