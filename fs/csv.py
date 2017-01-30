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

"""
>>> q = pdq.Query(file='test/test.csv.tar.gz', member='test.csv')
<class '_csv.Error'>
[
  "iterator should return strings, not bytes (did you open the file in text mode?)"
]
Traceback:
  File "<stdin>", line 1, in <module>
  File "/home/nine/dev/pyrox/data/pdq.py", line 67, in __init__
    self.__data = self.mreader(**k).read()
  File "/home/nine/dev/pyrox/fs/csv.py", line 40, in read
    return [r for r in self.lines]
  File "/home/nine/dev/pyrox/fs/csv.py", line 40, in <listcomp>
    return [r for r in self.lines]
  File "/home/nine/dev/pyrox/fs/csv.py", line 36, in lines
    for line in csvr:
>>> 
"""
