"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

FILE - File Object, for reading normal files.
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





class TransformFile (File):
	"""
	EXPERIMENTAL!
	
	This class may not be here long; if it remains, it will almost
	certainly experience lots of changes.
	"""
	def __init__(self, transformer, *a, **k):
		self.__transform = transformer
		File.__init__(self, *a, **k)
	
	def read(self, *a, **k):
		"""
		The read() method's results are transformed using the transformer
		passed to the constructor. For example, if JSON text describes a
		dict, the TransformJson transformer will convert it to a dict and
		return that dict.
		"""
		return self.__transform.fromtext(File.read(self, *a, **k))
	
	def write(self, data, *a, **k):
		"""
		Pass data as expected by this file's transformer. For example, 
		if the TransformJson transformer was specified to the constructor
		then you can pass string, dict, list, or any object parsable by
		the json.dumps() method and that will be transformed to text then
		written to this file.
		"""
		File.write(self, self.__transform.totext(data), *a, **k)
	
	def reader(self, *a, **k):
		"""
		Stores the read object in a PseudoReader. 
		"""
		return PseudoReader(self.read(*a, **k))
	
	# should PseudoWriter accept one object to be written?
	# writeline could add a member to a dict or list object! omg,
	# it could use cursor to manipulate nearly anything! how cool
	# would that be?
	def writer(self, *a, **k):
		raise NotImplementedError()





class PseudoReader(object):
	"""
	EXPERIMENTAL!
	This class may not be here long; if it remains, it will almost
	certainly experience lots of changes.
	
	Holds a data object to be returned in its entirety on the first
	read (by any means - iter, read, lines, or readlines). Subsequent 
	attempts to read will result in an Exception - which currently is
	EOFError, though that may change in the future;
	
	TO-DO: What should that exception be?
	"""
	def __init__(self, data):
		self.__data = data
	
	# stream methods
	@property
	def stream(self):
		raise NotImplementedError()
	
	def close(self):
		self.__data = None
	
	# reading stream methods
	@property
	def lines(self):
		yield self.read()
	
	def __iter__(self):
		return self.lines
	
	def read(self, *a):
		try:
			if not self.__data:
				raise EOFError() # or StopIteration? or what?
			return self.__fp.read(*a)
		finally:
			self.__data = None
	
	def readline(self):
		return self.read()
	
	
