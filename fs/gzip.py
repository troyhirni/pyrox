"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

GZIP - Covers gzip files.

"""


from .bfile import *


class Gzip(ByteFile):
	"""Gzip file support."""
	@property
	def gzfactory(self):
		try:
			return self.__gzfactory
		except:
			self.__gzfactory = Factory("gzip.GzipFile")
			return self.__gzfactory
	
	def open(self, mode='rb', **k):
		ok = Base.kcopy(k, 'mode compresslevel fileobj mtime')
		return self.gzfactory(self.path, mode, **ok)


