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

from ..ext.ext_csv import *


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
	
	def __init__(self, stream, dialect=None, *a, **k):
		"""
		Pass a `stream` to text data.
		
		* PARSING OPTIONS *
		Pass a dialect (or string dialect selector) to select the exact
		dialect you want to use. The default is None, which will leave
		CSVReader free to "sniff" the stream text for the best chance of
		successful parsing. See below for details.
		
		When dialect is None (the default for CSVReader) the csv.Sniff
		class is used to "sniff" text from the csv stream to determine
		dialect settings that will likely produce valid results.
		
		Optionally, pass keyword argument `sniff`=False to disable the
		sniffer that's automatically triggered by this constructor. If
		not disabled (by sniff=False), sniff results are set as defaults
		for keywords passed to the reader.
		
		Set `sniff` to a positive integer if you want to control how many
		bytes are sniffed. (The default is 1024.)
		
		Optionally, pass keyword arguments matching a Dialect object's 
		attributes. These are passed directly to the csv.reader as 
		keyword arguments. Keyword arguments you specify overrule any
		results of an automatic sniff.
		
		DIALECT KEY:      DEFAULT:
		delimiter         ','
		doublequote       1
		escapechar        None
		lineterminator    '\r\n'
		quotechar         '"'
		quoting           0
		skipinitialspace  0
		strict            0
		
		Pass sniff=False and no csv-related keyword arguments if you want
		the default csv.reader action.
		"""
		
		#
		# Pass stuff up first - not sure what will happen below, but the
		# encoding gets popped before sending to csv.reader() and I don't
		# want to miss storing that (if only for reference).
		#
		Reader.__init__(self, stream, **k)
		
		#
		# Get rid of encoding-related stuff csv reader doesn't want.
		# Probably won't need the return values here, but I'll leave it
		# for now, just in case.
		#
		enc = Base.kpop(k, 'encoding')
		err = Base.kpop(k, 'errors')
		
		# If dialect is specified, ignore all dialect-related keywords.
		if not dialect:
			
			# If sniff is disabled (sniff=None) then.. well.. don't sniff!
			# Otherwise, do.
			k.setdefault('sniff', 1024)
			sniff = Base.kpop(k, 'sniff') or None
			if sniff:
				dialect = Sniffer().sniff(stream.read(1024))
				stream.seek(0)
		
		# make the csv reader
		self.__csv = reader(stream, *a, **k)
		
		# p2/p3
		self.next = self.__next__
		
		# replace read, readline
		self.read = self.readlist
		self.readline = self.__next__ # this needs to move to fs.Reader
		
		# REMOVE ME (after debugging)!!!
		self.cr = self.__csv
		
	
	def __iter__(self):
		return self.lines
	
	def __next__(self):
		return next(self.lines)
	
	@property
	def lines(self):
		csvr = self.__csv
		if self.ek:
			for line in csvr:
				yield line.encode(**self.ek)
		else:
			for line in csvr:
				yield line
	
	# READ
	def readlist(self, *a):
		return [r for r in self]
		




class CSVWriter(Writer):
	
	def __init__(self, stream, *a, **k):
		Writer.__init__(
				Base.create('csv.writer', stream, *a, **k)
			)
	
	def write(self, data):
		self.stream.write(data)



