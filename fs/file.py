"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

DIR - Directory

"""


from . import *


import os


class File(ImmutablePath):
	"""Represents a file."""
	
	def __init__(self, path, **k):
		"""Pass path to file. Keywords apply as to Path.expand()."""
		try:
			Path.__init__(self, k.get('file', path), **k)
		except:
			raise ValueError('fs-invalid-path', xdata(path=path, k=k))
	
	# HEAD
	def head(self, lines=12, **k):
		"""Top lines of file. Any kwargs apply to codecs.open()."""
		a = []
		k.setdefault('mode', 'r')
		k.setdefault('encoding', DEF_ENCODE)
		with self.open(**k) as fp:
			for i in range(0, lines):
				a.append(fp.readline())
		return ''.join(a)
	
	# READ
	def read(self, mode='r', **k):
		"""Open and read file at self.path. Default mode is 'r'."""
		with self.open(mode, **k) as fp:
			return fp.read()
	
	# WRITE
	def write(self, data, mode='w', **k):
		"""Open and write data to file at self.path."""
		with self.open(mode, **k) as fp:
			try:
				fp.write(data)
			except TypeError:
				fp.write(unicode(data))
	
	# TOUCH
	def touch(self, times=None):
		"""Touch this file."""
		with open(self.path, 'a'):
			os.utime(self.path, times)  
