"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

FILTER - Filters for Streams


         EXPERIMENTAL - UNDER CONSTRUCTION





import csv, io
cdata = "1,2,3\n4,5,6\n7,8,9\n"
ss = io.StringIO(cdata)
ss.next = ss.readline
cv = csv.reader(ss)




"""


from .. import *


class Filter(object):
	"""
	Base filter; Doesn't even cost an extra to read - reads from the 
	stream object that was passed to it.
	"""
	def __init__(self, stream):
		self.__stream = stream
	
	def __iter__(self):
		return self.lines
	
	@property
	def stream(self):
		return self.__stream
	
	@property
	def lines(self):
		for line in self.stream:
			yield line
	
	def readline(self):
		for x in self.lines:
			return x

	def read(self, *a, **k):
		return self.stream.read(*a, **k)




class FilterCSV(Filter):
	"""
	
	"""
	def __init__(self, stream, *a, **k):
		"""Pass a csv.reader stream."""
		self.__csvreader = Base.ncreate('csv.reader', stream, *a, **k)
		Filter.__init__(self, self.__csvreader)
	
	
