import os.path
from distutils.dir_util import copy_tree
import git


def CopyCoreHere(dest):
    print(dest)
    path = dest + "/core"
    if not os.path.exists(path):
        git.Repo.clone_from("https://github.com/zheld/geyser_core_go.git", dest + '/core')
