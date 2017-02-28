"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

FILE - File Object, for reading normal files.
"""


from . import *
from . import opener
	


#
# FILE
#
class File(FileBase):
	"""Represents a file."""
	
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
	
	
	# OPEN
	def open(self, mode='r', **k):
		"""
		Open file at self.path with an fs.opener Opener object. 
		
		ENCODING VS BYTES:
		Returns an open file pointer; Close it when you're done. 
		 * To read binary data: theFile.read(mode="rb")
		 * To read unicode text: theFile.read(encoding="<encoding>")
		 * To write binary data: theFile.write(theBytes, mode="wb")
		 * To write unicode text: theFile.write(s, encoding="<encoding>")
		
		It's important to pass [a mode containing 'b'] or [an encoding] 
		to the open methods. Don't rely on defaults or results may funky.
		Pass mode only when you want bytes to be returned. Use 'encoding' 
		only when you want text to be returned.
		
		MODE:
		With mode "r" or "w", i/o ops automatically read/write the BOM
		where appropriate (assuming you specified the right encoding). 
		However, if you have bytes to save as encoded text, you can 
		do the following so as to save BOM and bytes as already encoded:
			>>> theFile.write(theBytes, mode="wb")
		
		This insures that a byte string (already encoded) is written 
		"as-is", including the BOM if any, and can be read by:
			>>> s = theFile.read(encoding="<encoding>")
		
		DEFAULT ENCODING:
		A default encoding (and `errors`) can be specified when creating
		this object. Any encoding or errors keyword specified to open()
		overrides that.
		    
		    f = File('my/file.txt', encoding='utf32')
		    f.open() # uses default, utf32
		    f.open(encoding='ascii') # uses ascii
		
		NOTE - ON EARLY PYTHON VERSION COMPATABILITY: 
		The opener will, for earlier versions of python, ignore 
		unsupported keyword arguments, but also will NOT provide the
		features rejected keyword args would have specified.
		"""
		# binary
		if 'b' in mode:
			return self.opener.open(self.path, mode, **k)
		
		# text
		else:
			# apply any specified default encoding-related params
			self.applyEncoding(k)
			
			# return the open file stream
			return self.opener.open(self.path, mode, **k)
	
	
	# HEAD
	def head(self, lines=12, **k):
		"""Top lines of file. Any kwargs apply to opener.open()."""
		a = []
		k.setdefault('mode', 'r')
		with self.open(**k) as fp:
			for i in range(0, lines):
				a.append(fp.readline())
		return ''.join(a)
	
	
	# READ
	def read(self, mode='r', **k):
		"""
		Open and read file at self.path. Default mode is 'r'.
		"""
		with self.open(mode, **k) as fp:
			return fp.read()
	
	
	# WRITE
	def write(self, data, mode='w', **k):
		"""
		Open and write data to file at self.path. Default mode is 'r'.
		"""
		with self.open(mode, **k) as fp:
			fp.write(data)
	
	
	# READER
	def reader(self, **k):
		"""
		Return a basic stream `Reader` instance.
		
		All arguments are passed by keyword. To create a Reader using an
		existing stream object, specify that stream using a `stream`
		keyword argument. The stream must implement read(), readline() 
		and the line generator.
		
		If `stream` is not specified, the file this object represents is
		opened (using keyword `mode`, if supplied) and the opened stream
		is passed. The default mode is "r".
		"""
		try:
			# if stream is given, send kwargs directly to Reader()
			return Reader(k.pop('stream'), **k)
		except KeyError:
			# get stream from self.open()
			k.setdefault('mode', 'r')
			ek = self.extractEncoding(k) if 'b' in k['mode'] else {}
			return Reader(self.open(**k), **ek)
	
	
	# WRITER
	def writer(self, **k):
		"""
		Just like `reader` except that its default `mode` keyword value 
		defaults to "w" instead of "r", so it writes instead of reads.
		
		r = File('infile.txt').reader()
		w = File('outfile.txt').writer()
		w.write(r.read())
		"""
		try:
			# if stream is given, send kwargs directly to Writer()
			return Writer(k.pop('stream'), **k)
		except KeyError:
			# ...else get stream from self.open()
			k.setdefault('mode', 'w')
			ek = self.extractEncoding(k) if 'b' in k['mode'] else {}
			return Writer(self.open(**k), **ek)





#
# MEMBER FILE - Base class for Tar and Zip file wrappers.
#
class MemberFile(File):
	"""
	Abstract class defines required `names` and `members` properties,
	which must be implemented by subclasses. 
	
	MemberFile is the base for tar.Tar and zip.Zip file wrappers.
	"""
	
	@property
	def names(self):
		"""EXPERIMENTAL"""
		raise NotImplementedError("abstract-method-required")
	
	@property
	def members(self):
		"""EXPERIMENTAL"""
		raise NotImplementedError("abstract-method-required")



