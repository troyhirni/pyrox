"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

ZIP - Covers zip files.


"""

import zipfile
from .file import *


class Zip(File):
	"""
	Read and write .zip files.
	
	Zip file works differently from other File-based classes in that 
	its open method is not available for reading unziped data from the
	file.
	"""
	
	def __init__(self, path, **k):
		"""Pass path to file. Keywords apply as to base.Path.expand()."""
		Path.__init__(self, k.get('zip', path), **k)
		with zipfile.ZipFile(self.path, 'w') as z:
			z.close()
	
	@property
	def names(self):
		"""Returns self.namelist()"""
		return self.namelist()
	
	def namelist(self):
		with zipfile.ZipFile(self.path, 'r') as z:
			nn = z.namelist()
			z.close()
			return nn
	
	def read(self, zpath):
		with zipfile.ZipFile(self.path, 'r') as z:
			r = z.read(zpath)
			z.close()
			return r
	
	def write(self, zpath, data, mode='a'):
		"""
		Write data to zpath within the zip file. Default mode is 'w'; to
		append more files, use mode='a'.
		"""
		with zipfile.ZipFile(self.path, mode) as z:
			z.writestr(zpath, data)
			z.close()


