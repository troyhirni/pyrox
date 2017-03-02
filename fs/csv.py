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


CSV_SNIFF_MIN = 1024









class CSV(File):
	"""
	EXPERIMENTAL
	
	
	"""
	
	# READ
	def read(self, data=None, mode='r', **k):
		return CSVReader(self.open(mode, **k)).read()
	
	
	# WRITE
	def write(self, data=None, mode='w', **k):
		if 'text' in k:
			text = k.pop('text')
			File.write(self, k['text'], mode, **k)
		elif isinstance(data, basestring):
			File.write(self, data, mode, **k)
		else:
			w = CSVWriter(self.open(mode, **k), **k).write(data)
			w.write(data)
	
	
	# READER
	def reader(self, **k):
		"""
		Returns a reader for the file this object represents (self.path)
		
		Pass keyword arguments:
		 - encoding = encoding with which to decode binary to unicode
		 - errors   = optional - how to handle encoding errors
		 - mode     = optional - mode (default 'rb') 

		To create with a stream, pass keyword argument:
		 - stream = A byte or text stream
		"""
		# pop all these so csv reader can have the rest of the kwargs
		mode = k.pop('mode', None)
		stream = k.pop('stream', None)
		
		if stream:
			return CSVReader(stream, **k)
		else:
			return CSVReader(self.open(mode or 'rb'), **k)
	
	
	# WRITER
	def writer(self, **k):
		"""
		Return a CSVWriter object pointing to this file.
		"""
		mode = k.pop('mode', None)
		stream = k.pop('stream', None)
		
		if stream:
			return CSVReader(stream, **k)
		else:
			return CSVReader(self.open(mode or 'wb'), **k)




class CSVReader(Reader):
	"""
	EXPERIMENTAL
	
	The CSVReader is very sensitive to encoding across python 2/3. It
	currently yields string results for every field - bytes in python 2
	and unicode strings for python 3.
	"""
	
	def __init__(self, stream, **k):
		"""
		Pass a stream that produces lines of csv data. The stream may
		produce text as bytes or unicode.
		
		ALWAYS PASS AN ENCODING!
		Always pass the correct encoding so that bytes may be converted
		to unicode if necessary, or so that unicode text may be converted
		to bytes if necessary.
		
		 * When the stream produces bytes, the encoding may be necessary 
		 to if the csv.reader object requires unicode.
		
		 * When the stream produces unicode characters, the encoding may 
		   be necessary to encode the bytes if the csv.reader object 
		   requires bytes.
		
		Passing the encoding gives CSVReader what it needs to work in 
		either python 2 or 3.
		"""
		
		# Extract encoding kwargs first! They MUST NOT reach the reader.
		ek = EncodingHelper(encoding='utf8').extractEncoding(k)
		
		# make sure we have a seekable stream
		try:
			stream.seek(0)
		except:
			# I don't want to extract to a tempfile - at least not yet -
			# so if it's a zip file (or some stream that can't seek) then 
			# we need to read the whole file up front.
			buf = Buffer()
			buf.write(stream.read())
			stream = buf.reader()
		
		
		# --- at this point, stream is seekable ---
		
		
		# default sniff can be overridden with values > 1024
		try:
			sniff = k.pop('sniff')
			if sniff < CSV_SNIFF_MIN:
				sniff = CSV_SNIFF_MIN
		except:
			sniff = CSV_SNIFF_MIN
		
		# sniff for a Dialect object and to detect stream data type
		dialect = None
		try:
			# first assume it's a unicode stream
			stream.seek(0)
			coder = ReadCoder(stream, encode=k.get('encoding', DEF_ENCODE))
			dialect = Sniffer().sniff(coder.read(sniff))
			stream.seek(0)
			self.__csv = reader(coder, dialect, **k)
			x = self.__next__()#test
		except TypeError as eencode:
			"""
			eencode = xdata(
				stream=stream, coder=coder, dialect=dict(dialect.__dict__)
			)
			"""
			# if that fails, try it as a byte stream
			stream.seek(0)
			coder = ReadCoder(stream, decode=k.get('encoding', DEF_ENCODE))
			dialect = Sniffer().sniff(coder.read(sniff))
			stream.seek(0)
			self.__csv = reader(coder, dialect, **k)
			try:
				x=self.__next__()#test
			except Exception as ex:
				raise type(ex)('create-reader-fail', xdata(
					stream=stream, coder=coder, dialect=dialect.__dict__
				))
		
		# ALWAYS RESET TO ZERO
		stream.seek(0)
		
		#
		# replace some methods (for speed)
		#
		self.readline = self.__next__
		self.next = self.__next__
	
	
	# ITER
	def __iter__(self):
		return self.lines
	
	# NEXT
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
		




class CSVWriter(Writer):
	"""
	EXPERIMENTAL
	
	Use writeline (alias to writerow) to write individual lines (rows)
	into a csv stream.
	
	Use write (alias to writelines) to write a list of lists to the 
	stream.
	"""
	
	def __init__(self, stream, *a, **k):
		Writer.__init__(self, stream)
		self.__csv = Base.create('csv.writer', stream, *a, **k)
		self.writeline = self.writerow
		self.writelines = self.write
	
	
	def write(self, data):
		for row in data:
			self.__csv.writerow(data)
	
		
	def writerow(self, data):
		self.__csv.writerow(data)
