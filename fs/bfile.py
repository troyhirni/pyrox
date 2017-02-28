"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

FILE - File Object, for reading normal files.
"""


from .file import *





#
# BYTE FILE - BZ2, GZIP
#
class ByteFile(File):
	"""
	Base class for files that work with bytes, such as tar, gzip, and 
	bzip2 files. When unicode strings are passed to the write() method,
	`encoding` (and, optionally, `errors`) must be supplied by keyword.
	When passed to read(), bytes will be encoded before being returned.
	"""
	
	
	# READ
	def read(self, mode='rb', **k):
		"""Open and read file at self.path. Default mode is 'r'."""
		# If any encoding-related arguments were provided, apply them
		# to the data AFTER reading.
		ek = self.extractEncoding(k)
		with self.open(mode) as fp:
			return fp.read(**k).decode(**ek) if ek else fp.read()
	
	
	# WRITE
	def write(self, data, mode='wb', **k):
		"""
		Open and write byte data to file at self.path. Default mode is 
		"wb", but can be overridden (typically by subclasses) if needed.
		
		Regardless of arguments, any encoding arguments cause the given
		data to be encoded before writing (so don't pass both bytes as 
		data AND an encoding - you'll only get an error.
		"""
		# If any encoding-related arguments were provided, apply them
		# to the data BEFORE writing; do NOT let them go to open()!
		ek = self.extractEncoding(k)
		with self.open(mode, **k) as fp:
			fp.write(data.encode(**ek) if ek else data)
	
	
	# READER
	def reader(self, **k):
		"""
		If passed, all bytes will be translated to the encoding given by
		an optional `encoding` keyword argument.
		"""
		k.setdefault('mode', 'rb')
		self.applyEncoding(k)
		return File.reader(self, **k)
	
	# WRITER
	def writer(self, **k):
		"""
		If an `encoding` keyword argument is specified, text given to the
		various write methods will be decoded before being written.
		"""
		k.setdefault('mode', 'wb')
		self.applyEncoding(k)
		return File.writer(self, **k)
