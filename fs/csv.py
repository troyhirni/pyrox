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
		Returns a reader for the file this object represents (self.path)
		
		Pass keyword arguments:
		 - encoding = encoding with which to decode binary to unicode
		 - mode     = optional mode (default, 'rt') 

		To create with a stream, pass keyword argument:
		 - stream = A byte or text stream
		"""
		# pop all these so csv reader can have the rest of the kwargs
		mode = Base.kpop(k, 'mode')
		stream = Base.kpop(k, 'stream')
		
		if stream:
			return CSVReader(stream, **k)
		else:
			# remove mode from kwargs so CSVReader doesn't receive it
			return CSVReader(self.open(mode or 'rt'), **k)





class CSVReader(Reader):
	
	def __init__(self, stream, *a, **k):
		
		enc = Base.kpop(k, 'encoding') or DEF_ENCODE
		Reader.__init__(self, stream, encoding=enc)
		
		self.__dec = Base.create('codecs.iterdecode', stream, enc)
		self.__csv = Base.create('csv.reader', self.__dec, *a, **k)
	
	def __iter__(self):
		return self.lines
	
	@property
	def lines(self):
		csvr = self.__csv
		for line in csvr:
			yield line
	
	# READ
	def read(self, *a):
		return [r for r in self.lines]
	
	# READLINE
	def readline(self):
		try:
			return next(self.lines)
		except:
			return self.lines.next()





class CSVWriter(Writer):
	
	def __init__(self, stream, *a, **k):
		Reader.__init__(
				Base.create('csv.writer', stream, *a, **k)
			)
	
	def write(self, data):
		self.stream.write(data)



