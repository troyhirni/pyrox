"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

TRANSFORM FILE - File Object, for structured text file io.

Use TransformFile objects to read text files which describe objects
that can be transformed from data to text or from text to data by a 
data.transform.Transform object.
"""


from .file import *


class TransformFile (File):
	"""
	Use TransformFile objects to read text files which describe
	objects (such as json text files).
	
	The first argument to TransformFile must be a data.transform object
	to convert the file's text to a python object. Additional arguments
	are those required by the File constructor.
	
		from px.fs import file
		from px.data import transform
		
		jsonTran = data.transform.TransformJson()
		jsonfile = file.TransformFile(jsonTran, 'test/test.json')
		jsonfile.write(dict(value1="That's valuable!", ix=9))
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
		Stores the parsed object in a DataReader. 
		"""
		return DataReader(self.read(*a, **k))
	
	# should PseudoWriter accept one object to be written?
	# writeline could add a member to a dict or list object! omg,
	# it could use cursor to manipulate nearly anything! how cool
	# would that be?
	def writer(self, *a, **k):
		raise NotImplementedError()




#
# DATA STREAM IMMITATORS
#

class DataReader(object):
	"""
	Implements Reader, but for a data object rather than a stream.
	
	Holds a data object to be returned in its entirety on the first
	read (by any means - iter, read, lines, or readlines). Subsequent 
	attempts to read will result in an Exception - which currently is
	EOFError, though that may change in the future;
	
	TO-DO: What should that exception be?
	"""
	def __init__(self, data):
		self.__data = data
	
	def __iter__(self):
		return self.lines
	
	# stream methods
	@property
	def stream(self):
		raise NotImplementedError()
	
	# reading stream methods
	@property
	def lines(self):
		yield self.read()
	
	def read(self, *a):
		if self.__data:
			try:
				return self.__data
			finally:
				self.__data = None
		else:
			raise EOFError() # or StopIteration? or what?
	
	def readline(self):
		return self.read()
	
	def close(self):
		self.__data = None





class DataWriter(Stream):
	"""
	Implements Writer, but for a data object rather than a stream.
	
	Holds the object that will convert the object to its proper format
	and write it to wherever it should be written.
	"""
	def __init__(self, obj, *a, **k):
		self.__obj = data
		self.__a = a
		self.__k = k
	
	def write(self, data):
		return self.stream.write(data, *self.__a, **self.__k)
	
	def writeline(self, data):
		return self.stream.writeline(data, *self.__a, **self.__k)

