"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

CSV - File and Reader for CSV        *** EXPERIMENTAL ***

CSV works pretty well, but has some quirks that need to be worked 
out. Write doesn't work; csv has to be written as text; Read works 
great, but in python 2 it reads bytes, while in python 3 it reads 
unicode strings. So far all attempts to unify the results have 
failed. I'll keep trying.

NOTE: This module imports * from python's csv module, so all the
      csv constants are available.

ALSO: For now, CSV.writer() falls back to the default File.writer,
      so csv has to be written as text. Once I figure out how to make
      it work, CSVWriter will probably handle either text or list as
      arguments to write() and writelines().
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
		 - mode     = optional - mode (default 'rt') 

		To create with a stream, pass keyword argument:
		 - stream = A byte or text stream
		"""
		# pop all these so csv reader can have the rest of the kwargs
		mode = k.pop('mode', None)
		stream = k.pop('stream', None)
		
		if stream:
			return CSVReader(stream, **k)
		else:
			return CSVReader(self.open(mode or 'rt'), **k)
	
	def write(self, data=None, mode='w', **k):
		if 'text' in k:
			text = k.pop('text')
			File.write(self, k['text'], mode, **k)
		elif isinstance(data, basestring):
			File.write(self, data, mode, **k)
		else:
			w = CSVWriter(self.open(**k), **k).write(data)
			w.write(data)
	



class CSVReader(Reader):
	
	"""
	# I need some way in python 2 to get the bytes to unicode before 
	# they're read. I want both p2 and p3 to get unicode values in the
	# strings contained by each line's array.
	def filterstream(self, stream, *a, **k):
		ek = self.extractEncoding(k)
		return Filter(stream, pxbytes.decode, **ek)
	
	NO - I need to give up on trying to import csv from non-text files.
	     This is a waste of time for now. I'm missing something about 
	     it and I don't want to spend another month trying to make it
	     work. It's not worth it.
	     
	     Someday the answer may come to me. Until then, CSVReader only
	     works with text files.
	"""
	
	
	def __init__(self, stream, dialect=None, *a, **k):
		"""
		Pass a `stream` to text data.
		
		* PARSING OPTIONS *
		Pass a dialect (or string dialect selector) to select the exact
		dialect you want to use. The default is None, which will leave
		CSVReader free to "sniff" the stream text for the best chance of
		successful parsing.
		
		When dialect is None (the default for CSVReader) the csv.Sniff
		class is used to "sniff" text from the csv stream to determine
		dialect settings that will likely produce valid results.
		
		Optionally, pass keyword argument sniff=False to disable the
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
		"""
		
		#
		# INIT - most of the time this will be the only init, but in the
		#        case of streams that can't "seek", a buffer stream is
		#        created (and the entire source stream is read into it)
		#        so that the file can be sniffed then set back to zero.
		#        NOTE: This happens for zip.Zip readers, seem unable to 
		#              be unable seek().
		#
		Reader.__init__(self, stream, **k)
		
		# If dialect is specified, ignore all dialect-related keywords.
		if not dialect:
			
			# If sniff is disabled (sniff=None) then.. well.. don't sniff!
			# Otherwise, do.
			k.setdefault('sniff', 1024)
			sniff = int(k.pop('sniff', None) or 0)
			if sniff and sniff >= 1:
				try:
					stream.seek(0) # throws an error for zip (which can't seek)
					dialect = Sniffer().sniff(stream.read(sniff))
					stream.seek(0)
				except:
					# if the stream can't seek, it's read completely into a 
					# BytesIO and that stream is used instead to sniff.
					try:
						bstream = Base.create('io.BytesIO', stream.read())
					except:
						bstream = Base.create('io.StringIO', stream.read())
					
					# Store the source in an fs.Stream object so it will be
					# closed when this object is done.
					self.__source = Stream(stream)
					stream = bstream
					
					# Finally, get the dialect and reset the stream to the
					# start of the file.
					dialect = Sniffer().sniff(stream.read(sniff))
					stream.seek(0)
					
					#
					# RE-INIT!
					#  - Now there's a new stream object (bstream) so the 
					#    superclass needs to hold on to that instead of the
					#    original source stream.
					#
					Reader.__init__(self, stream, **k)
		
		
		# make the csv reader
		if dialect:
			self.__csv = reader(stream, dialect, *a, **k)
		else:
			self.__csv = reader(stream, *a, **k)
		
		# replace readline
		self.readline = self.__next__
		
	
	def __iter__(self):
		return self.lines
	
	def __next__(self):
		return next(self.lines)
	
	# LINES
	@property
	def lines(self):
		csvr = self.__csv
		for line in csvr:
			yield line
	
	# READ
	def read(self, *a):
		return [r for r in self]
		



"""
class CSVWriter(Writer):
	
	def __init__(self, stream, *a, **k):
		Writer.__init__(
				Base.create('csv.writer', stream, *a, **k)
			)
	
	def write(self, data):
		self.stream.writerow(data)
"""


