"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

CSV - File and Reader for CSV        *** EXPERIMENTAL ***

The CSV class is supposed to be a File class with a different reader.
All other methods are the same, but the reader returns each row as a
list instead of text. UNFORTUNATELY.... that's not what it is. I'm 
not really sure what it is, but it's not that. I may trash it.
"""


from .file import *



class CSV(File):
	
	def reader(self, **k):
		"""
		Returns a reader for the file this object represents (self.path)
		
		Pass keyword arguments:
		 - encoding = encoding with which to decode binary to unicode
		 - errors   = optional - how to handle encoding errors
		 - mode     = optional - mode (default, 'rt') 

		To create with a stream, pass keyword argument:
		 - stream = A byte or text stream
		"""
		# pop all these so csv reader can have the rest of the kwargs
		mode = Base.kpop(k, 'mode')
		stream = Base.kpop(k, 'stream')
		
		if stream:
			return CSVReader(stream, **k)
		else:
			return CSVReader(self.open(mode or 'rt'), **k)

	
	def write(self, data=None, mode='w', **k):
		"""
		If a `text` keyword argument is given, the `data` argument is
		ignored and the value of the `text` kwarg is written as-is, as
		text.
		
		If the `data` argument is given as a string type, its value is
		written as-is, as text.
		
		If the `data` argument type is anything other than a string, it
		must be something acceptable to python's csv.writer constructor.
		The csv.writer will write the data to this file as it sees fit.
		(See python's csv module documentation.)
		"""
		if 'text' in k:
			text = Base.kpop(k, 'text')
			File.write(self, k['text'], mode, **k)
		elif isinstance(data, basestring):
			File.write(self, data, mode, **k)
		else:
			w = CSVWriter(self.open(**k), **k).write(data)
			w.write(data)





class CSVReader(Reader):
	
	def __init__(self, stream, *a, **k):
		
		Reader.__init__(self, stream, **k)
		
		# get rid of encoding-related stuff csv reader doesn't want
		enc = Base.kpop(k, 'encoding')
		err = Base.kpop(k, 'errors')
		
		self.__dec = Base.create('codecs.iterdecode', stream, enc)
		self.__csv = Base.create('csv.reader', self.__dec, *a, **k)
	
	def __iter__(self):
		return self.lines
	
	@property
	def lines(self):
		csvr = self.__csv
		if self.encode:
			for line in csvr:
				yield line.encode(self.encode)
		else:
			for line in csvr:
				yield line.encode(self.encode)
	
	# READ
	def read(self, *a):
		return [r for r in self.lines]
	
	# READLINE
	def readline(self):
		try:
			return next(self.lines)
		except AttributeError:
			return self.lines.next()





class CSVWriter(Writer):
	
	def __init__(self, stream, *a, **k):
		Writer.__init__(
				Base.create('csv.writer', stream, *a, **k)
			)
	
	def write(self, data):
		self.stream.write(data)



