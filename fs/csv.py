"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

CSV - File and Reader for CSV        *** EXPERIMENTAL ***

The CSV class is basically just a File class with a different reader.
All other methods are the same, but the reader returns each row as a
list instead of text. 

"""


from .file import *



class CSV(File):
	
	def reader(self, mode='r', *a, **k):
		return CSVReader(self.open(mode='r'), *a, **k)





class CSVReader(Reader):
	
	def __init__(self, stream, *a, **k):
		Reader.__init__(self, stream)
		self.__csvreader = Base.create('csv.reader', stream, *a, **k)
	
	def __iter__(self):
		return self.lines
	
	@property
	def lines(self):
		csvr = Base.create('csv.reader', self.stream)
		for line in csvr:
			yield line

	def read(self, *a):
		return [r for r in self.lines]
	
	def readline(self):
		self.__lines = self.lines
		#self.__next = self.lines.next
		try:
			return next(self.__lines)  # python3
		except:
			return self.__lines.next() # python2

