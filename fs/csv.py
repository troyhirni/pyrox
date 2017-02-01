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
	
	def reader(self, **k):
		"""
		Default mode is 'rt'
		"""
		mode = Base.kpop(k, 'mode')
		stream = Base.kpop(k, 'stream')
		#encoding = 
		
		if stream:
			return CSVReader(stream, **k)
		else:
			# remove mode from kwargs so CSVReader doesn't receive it
			return CSVReader(self.open(mode or 'rt'), **k)





class CSVReader(Reader):
	
	def __init__(self, stream, *a, **k):
		
		#stream = Base.create('csv.reader', stream, *a, **k)
		#Reader.__init__(self, stream)
		
		# why would i do this?
		Reader.__init__(self, stream)
		self.__csvreader = Base.create('csv.reader', stream, *a, **k)
	
	def __iter__(self):
		return self.lines
	
	@property
	def lines(self):
		#csvr = Base.create('csv.reader', 'rt', self.stream)
		csvr = self.__csvreader
		for line in self.__csvreader:
			yield line

	def read(self, *a):
		return [r for r in self.lines]
	
	# TODO: speed enhancement
	def readline(self):
		return next(self.lines)
		
		"""
		self.__lines = self.lines
		try:
			return next(self.__lines)  # python3
		except:
			return self.__lines.next() # python2
		"""




class CSVWriter(Writer):
	
	def __init__(self, stream, *a, **k):
		Reader.__init__(
				Base.create('csv.writer', stream, *a, **k)
			)
	
	def write(self, data):
		self.stream.write(data)



