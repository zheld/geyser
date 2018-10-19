import os

from generator.generator_item import GeneratorItem


class FSItem(GeneratorItem):
    # File System item

    def __init__(self, name, parent=None):
        super(FSItem, self).__init__(name, parent)
        # if the object has no parent, then the object is in the root directory
        parent_dir = self.parent.getPath() if self.parent else os.getcwd()
        if name:
            self.path = parent_dir + '/' + self.Name()
        else:
            self.path = parent_dir

    def getPath(self):
        return self.path

    def setPath(self, path):
        if self.Name():
            self.path = path + "/" + self.Name()
        else:
            self.path = path