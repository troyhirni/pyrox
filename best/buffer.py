"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyro project, distributed under the terms 
of the GNU Affero General Public License.

FS - File System Functionality

The base for pyro file system operations. Defines the Path object,
"""



def buffer():
	try:
		return Base.ncreate('io.BytesIO')
	except TypeError:
		return Base.ncreate('StringIO.StringIO')


def textbuffer():
	try:
		return Base.ncreate('io.StringIO')
	except TypeError:
		return Base.ncreate('StringIO.StringIO')
