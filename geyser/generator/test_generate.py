#!/usr/bin/env python
# coding=utf-8

from Python.package import Package
from FSItem.directory import Directory
from Python.pyfile import PyFile


core = Directory('test_core')
copy_original = PyFile('copy_original')

test_package = core.addPackage('test_package')
pf = test_package.addPyFile('active')
class_test = pf.addClass('test', 'Testo')
pf.addRowsBlock( 'import core' )
test_package.addCopyFile(copy_original, 'copy.py')
test_package.addSymLink(copy_original, 'sym_copy.py')


core.Build()

