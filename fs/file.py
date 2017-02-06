"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

FILE - File Object, for reading normal files.
"""


from . import *



#
# FILE
#
class File(ImmutablePath):
	"""Represents a file."""
	
	def __init__(self, path, **k):
		"""Pass path to file. Keywords apply as to Path.expand()."""
		try:
			ImmutablePath.__init__(self, k.get('file', path), **k)
		except:
			raise ValueError('fs-invalid-path', xdata(path=path, k=k))

	@property
	def opener(self):
		"""
		Return an `opener` object that opens a file stream to a file
		this path points to. This property is intended for internal use.
		Use the objects returned by the `reader()` and `writer()` methods
		to read from and write to files.
		"""
		try:
			return self.__opener
		except:
			self.__opener = opener.Opener()
			return self.__opener
	
	# READER
	def reader(self, **k):
		"""
		Returns a basic stream `Reader` instance, defined in the fs.path
		module. This `reader` method can be inherrited and used by any 
		file type wrapper whose open method produces a file-like object.
		Subclasses need only implement an open() method that returns a
		stream with `read`, `readline` methods, a line generator property,
		and support for iteration.
		
		All arguments are passed by keyword. Pass either:
		 * stream - a stream object that implements read(), readline()  
		            and the line generator;
		 * mode   - override the default mode, "r"
		
		Additional keywords are passed to the open method of an object 
		returned by the `File.opener` property. Such an opener will work
		from the earliest versions of python using the file() constructor,
		through the later versions using `open()` and `codecs.open()`, up
		to the most recent versions, which use the `io.open()` method.
		
		As far as kwargs go, defaults will always work (and usually best)
		for calls from project methods, so ftw it's usually just:
				r = File("path.txt").reader()
				r.read()
		
		Note, however, that some specialty classes (eg, from the `csv` 
		and `tfile` modules) implement specialty readers that return 
		python data objects (list, dict, etc...) so those will often need
		to be handled differently. See the help for each `Reader`.
		"""
		stream = Base.kpop(k, 'stream')
		if stream:
			return Reader(stream, **k)
		else:
			k.setdefault('mode', 'r')
			return Reader(self.open(**k), **k)
		
	
	# WRITER
	def writer(self, **k):
		"""
		Just like `reader` except that its default `mode` keyword value 
		defaults to "w" instead of "r", so it writes instead of reads.
		
		r = File('infile.txt').reader()
		w = File('outfile.txt').writer()
		w.write(r.read())
		"""
		stream = Base.kpop(k, 'stream')
		if stream:
			return Writer(stream)
		else:
			k.setdefault('mode', 'w')
			return Writer(self.open(**k))
	
	
	# OPEN
	def open(self, mode='r', **k):
		"""
		Open file at self.path with an fs.opener Opener object. 
		
		IMPORTANT:
		 * Returns an open file pointer; Close it when you're done. 
		 * To read binary data: theFile.read(mode="rb")
		 * To read unicode text: theFile.read(encoding="<encoding>")
		 * To write binary data: theFile.write(theBytes, mode="wb")
		 * To write unicode text: theFile.write(s, encoding="<encoding>")
		
		With mode "r" or "w", codecs automatically read/write the BOM
		where appropriate (assuming you specify the right encoding). 
		However, if you have text to save as encoded bytes, you can 
		do the following so as to save BOM and bytes as encoded:
			>>> theFile.write(theBytes, mode="wb")
		
		This insures that a byte string (already encoded) is written 
		"as-is", including the BOM if any, and can be read by:
			>>> s = theFile.read(encoding="<encoding>")
		"""
		# binary
		if 'b' in mode:
			return self.opener.open(self.path, mode, **k)
		
		# text
		else:
			k.setdefault('encoding', DEF_ENCODE)
			return self.opener.open(self.path, mode, **k)
	
	
	# READ
	def read(self, mode='r', **k):
		"""Open and read file at self.path. Default mode is 'r'."""
		with self.open(mode, **k) as fp:
			return fp.read()
	
	
	# WRITE
	def write(self, data, mode='w', **k):
		"""Open and write data to file at self.path."""
		with self.open(mode, **k) as fp:
			try:
				fp.write(data)
			except TypeError:
				k = Base.kcopy(k, 'encoding errors') or {}
				fp.write(unicode(data, **k))
	
	
	# HEAD
	def head(self, lines=12, **k):
		"""Top lines of file. Any kwargs apply to opener.open()."""
		a = []
		k.setdefault('mode', 'r')
		k.setdefault('encoding', DEF_ENCODE)
		with self.open(**k) as fp:
			for i in range(0, lines):
				a.append(fp.readline())
		return ''.join(a)





#
# BYTE FILE - BZ2, GZIP, TAR, ZIP
#
class ByteFile(File):
	
	def __init__(self, *a, **k):
		File.__init__(self, *a, **k)
	
	# WRITE
	def write(self, data, mode='wb', **k):
		"""Open and write data to file at self.path."""
		k = Base.kcopy(k, 'encoding errors')
		with self.open(mode) as fp:
			fp.write(data.encode(**k) if k else data)
	
	
	# READ
	def read(self, mode='rb', **k):
		"""Open and read file at self.path. Default mode is 'r'."""
		k = Base.kcopy(k, 'encoding errors') if k else {}
		with self.open(mode) as fp:
			return fp.read().decode(**k) if k else fp.read()

	"""
	def reader(self, **k):
		k.setdefault('mode', 'rb')
		return File.reader(self.open(**ok), **k)
	"""




#
# MEMBER FILE - TAR, ZIP
#
class MemberFile(File):
	pass



