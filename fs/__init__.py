"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyro project, distributed under the terms 
of the GNU Affero General Public License.

FS - File System Functionality

The base for pyro file system operations. Defines the Path object,
Stream Reader and Writer. This constitutes the bare necessities for 
reading and writing text files and for working with and getting info
about paths.
"""

from .. import *

import os, os.path as ospath



#
# PATH
#  - Base for fs module's classes.
#
class Path(object):
	"""Represents a file system path."""
	
	# INIT
	def __init__(self, path=None, **k):
		"""
		Pass the path this object refers to. Any additional keyword args
		will apply to the Path.expand() method, which is always called on
		this path immediately.
		"""
		self.__p = self.expand(k.get('path', path or '.'), **k)
		self.__n = ospath.normpath(self.__p).split(os.sep)[-1]
	
	# CALL - EXPERIMENTAL
	def __call__(self, path):
		"""
		Calling a Path object as a function returns a new Path object that
		points to its path "merged" with the (required) given `path`.
		"""
		return Path(self.merge(path))
	
	# REPR
	def __repr__(self):
		"""Object representation."""
		return str(type(self))
	
	# STR
	def __str__(self):
		"""The path as a string."""
		return self.path
	
	# UNICODE
	def __unicode__(self):
		"""The path as a unicode string (python 2 support)"""
		return unicode(self.path)
	
	
	# PROPERTIES
	
	@property
	def mime(self):
		"""Return a fs.mime.Mime object for this object's path."""
		return Base.ncreate('fs.mime.Mime', self.path)
	
	@property
	def parent(self):
		"""Return the path to this path's parent directory."""
		return ospath.dirname(self.path)
	
	@property
	def path(self):
		"""Return or set this path."""
		return self.getpath()
	
	@property
	def name(self):
		"""Return current path's last element."""
		return self.__n
	
	@path.setter
	def path(self, path):
		self.setpath(path)
	
	
	# METHODS
	
	def exists(self, path=None):
		"""True if path exists."""
		return ospath.exists(self.merge(path))
	
	def getpath(self):
		"""Return this object's path."""
		return self.__p
	
	def setpath(self, path):
		"""Set this object's path."""
		self.__p = path
		self.__n = ospath.normpath(path).split(os.sep)[-1]
	
	def isfile(self, path=None):
		"""True if path is a file."""
		return ospath.isfile(self.merge(path))
	
	def isdir(self, path=None):
		"""True if path is a directory."""
		return ospath.isdir(self.merge(path))
	
	def islink(self, path=None):
		"""True if path is a symbolic link."""
		return ospath.islink(self.merge(path))
	
	def ismount(self, path=None):
		"""True if path is a mount point."""
		return ospath.ismount(self.merge(path))
	
	def touch(self, path=None, times=None):
		"""Touch file at path. Arg times applies to os.utime()."""
		p = self.merge(path)
		with open(p, 'a'):
			os.utime(p, times)
	
	def merge(self, path):
		"""Returns the given path relative to self.path."""
		if not path:
			return self.path
		p = ospath.expanduser(path)
		if ospath.isabs(p):
			return ospath.normpath(p)
		else:
			p = ospath.join(self.path, p)
			return ospath.abspath(ospath.normpath(p))
	
	
	# DIR
	def dir(self, path=None):
		return Base.ncreate('fs.dir.Dir', self.merge(path))
	
	
	# WRAPPER
	def wrapper(self, **k):
		"""
		Returns a fs.File-based object wrapping the fs object at this
		path. The default for files whose mime type can't be matched 
		here is fs.file.File.
		"""
		mm = self.mime
		if self.isdir() or self.ismount():
			raise Exception('open-fail', xdata(
				path=self.path, reason='file-required', k=k
			))
		
		# Application
		if mm.type == 'application':
			
			# tar, tar.bz2, tar.gz, tgz
			if mm.subtype == 'x-tar':
				return Base.ncreate('fs.tar.Tar', self.path, **k)
			
			# zip
			elif mm.subtype == 'zip':
				return Base.ncreate('fs.zip.Zip', self.path, **k)
			
			# xlsx - for now, just use zip
			elif mm.subtype == 'vnd.openxmlformats-officedocument.spreadsheetml.sheet':
				return Base.ncreate('fs.zip.Zip', self.path, **k)
			
			# json
			elif mm.subtype == 'json':
				tj = Base.ncreate('data.transform.TransformJson')
				return Base.ncreate(
					'fs.tfile.TransformFile', tj, self.path, **k
				)
		
		# Text/enc 
		elif mm.type == 'text':
			
			# bz2 (plain, csv)
			if mm.enc == 'bzip2':
				if mm.subtype == 'plain':
					return Base.ncreate('fs.bzip.Bzip', self.path, **k)
				elif mm.subtype in ['csv', 'tab-separated-values']:
					return Base.ncreate('fs.csv.CSV', self.path, **k)
			
			# gzip
			elif mm.enc == 'gzip':
				if mm.subtype == 'plain':
					return Base.ncreate('fs.gzip.Gzip', self.path, **k)
				elif mm.subtype in ['csv', 'tab-separated-values']:
					return Base.ncreate('fs.csv.CSV', self.path, **k)
			
			# text csv	
			elif mm.subtype in ['csv', 'tab-separated-values']:
				return Base.ncreate('fs.csv.CSV', self.path, **k)
		
		# Default - for plain text or, as a default, any kind of file
		return Base.ncreate('fs.file.File', self.path, **k)
	
	
	
	# READER
	def reader(self, **k):
		"""
		Return a reader for this object's path based on the mime type of
		the file there. If this Path object points to a tar or zip file,
		a member keyword must specify the member to read. In such cases,
		the returned Reader object will be suitable to the mime type of
		the specified member - as far as is supported by the fs package.
		Currently that equates to: A csv reader for csv test, a JSON
		DataReader for json, or a plain `Reader` for all others.
		
		Encoding-related kwargs are extracted and sent to the reader when
		it's created. All other (not encoding-related) kwargs are used to
		create any wrappers that may be needed to create this reader. 
		
		NOTE: Do not specify a 'mode'; this method must always rely on
		      the default mode for the type of wrapper that represents 
		      the file at this path.
		"""
		
		# Wrapper gets no encoding-related kwargs - send them to the 
		# reader only (along with everything else).
		sk = EncodingHelper().sansEncoding(k)
		
		# Files with members will need to create a different kind of
		# object from what gets returned. Pop that key out of kwargs
		# before calling `wrapper`.
		member = k.pop('member', None)
		
		# now get the file wrapper object and return a reader
		wrapper = self.wrapper(**sk)
		
		
		# -- container wrapper handling (tar/zip) --
		
		# If member is passed, it is required; the file type wrapper must
		# have a 'names' property.
		if member:
			try:
				wrapper.names
			except Exception as ex:
				raise type(ex)('fs-reader-fail', xdata(k=k, path=self.path,
						reason='fs-non-container', member=member, wrapper=wrapper
					))
			
			# make sure the specified member exists in the tar/zip file
			if not member in wrapper.names:
				raise KeyError('fs-reader-fail', xdata(k=k, path=self.path,
						reason='fs-non-member', member=member, wrapper=wrapper
					))
			
			# get correct file class by calling wrapper on member
			mpath = Path(member, affirm=None)
				
			# get a wrapper suitable to the member's filename
			mwrap = mpath.wrapper()
			
			# get the original 'owner' stream for the memberwrapper to use
			ownerstream = wrapper.reader(member=member).detach()
			
			# REM: Readers can be sensitive to certain kwargs, especially
			#      for the CSVReader!
			return mwrap.reader(stream=ownerstream, **k)
		
		
		# -- non-contaner handling --
		return wrapper.reader(**k)
	
	
	@classmethod
	def expand(cls, path=None, **k): # EXPAND
		"""
		Returns an absolute path.
		
		Keyword 'affirm' lets you assign (or restrict) actions to be
		taken if the given path does not exist. 
		 * checkpath - default; raise if parent path does not exist.
		 * checkdir - raise if full given path does not exist.
		 * makepath - create parent path as directory if none exists.
		 * makedirs - create full path as directory if none exists.
		 * touch - create a file at the given path if none exists.
		
		To ignore all validation, pass affirm=None.
		"""
		OP = os.path
		if path in [None, '.']:
			path = os.getcwd()
		
		if not OP.isabs(path): # absolute
			path = OP.expanduser(path)
			if OP.exists(OP.dirname(path)): # cwd
				path = OP.abspath(path)
			else:
				path = OP.abspath(OP.normpath(path))
		
		v = k.get('affirm', "checkpath")
		if (v=='checkpath') and (not OP.exists(OP.dirname(path))):
			raise ValueError('no-such-path', {'path' : OP.dirname(path)})
		if v:
			if OP.exists(path):
				if (v=='checkdir') and (not OP.isdir(path)):
					raise ValueError('not-a-directory', {'path' : path})
			else:
				if (v=='checkdir'):
					raise ValueError('no-such-directory', {'path' : path})
				elif v in ['makepath', 'touch']:
					if not OP.exists(OP.dirname(path)):
						os.makedirs(OP.dirname(path))
					if v == 'touch':
						with open(path, 'a'):
							os.utime(path, None)
				elif (v=='makedirs'):
					os.makedirs(path)
		
		return path





#
# ENCODING HELPER
#
class EncodingHelper(object):
	"""
	Encoding helper stores a default encoding (optional) and provides
	some convenient properties and methods.
	"""
	def __init__(self, **k):
		# build the `ek` dict for easy passing of kwargs
		self.__ek = {}
		enc = k.pop('encoding', None)
		if enc:
			self.__ek = dict(encoding=enc)
			err = k.pop('errors', None)
			if err:
				self.__ek['errors'] = err
		
	
	def __call__(self, k):
		return self.setdefaults(k)
	
	@property
	def encoding(self):
		"""
		Encoding specified to constructor; used as default.
		"""
		return self.__ek.get('encoding')
	
	@property
	def errors(self):
		"""
		Encoding error handler specified to constructor; used as default.
		Eg, 'ignore', 'replace', 'xmlcharrefreplace', 'backslashreplace'.
		Default is None, the functional equivalent of 'strict'.
		"""
		return self.__ek.get('errors')
	
	@property
	def ek(self):
		"""
		Internal support for subclasses; A dict that provides any given
		`encoding` and/or `errors` values related to encoding/decoding
		read and written stream data. Returns an empty dict if no such
		values were specified to the Stream constructor.
		
		def openFile(path, **k):
			# create an encoding helper with default encoding
			helper = EncodingHelper(encoding='utf8')
			
			# extract the encoding from the helper
			ek = helper.extractEncoding(k)
			
			# send `encoding` kwarg, either the one given via **k or the
			# the default as specified to the `helper` constructor (if no
			# `encoding` is specified in **k.
			return open(path, **ek)
			
		fp1 = openFile('test.txt', encoding='ascii')
		"""
		return self.__ek
	
	
	# SANS-ENCODING
	def sansEncoding(self, k):
		"""
		Return a new dict with all keys except 'encoding' and 'errors'.
		This is useful if you need to pass kwargs that contain everything
		*except* the encoding and errors keys.
		"""
		r = {}
		for key in k:
			if key not in 'encoding errors':
				r[key] = k[key]
		return r
	
	
	# EXTRACT ENCODING
	def extractEncoding(self, k):
		"""
		Remove any `encoding` and `errors` keys from given dict `k`. 
		Returns a new dict with `encoding` and `errors` set to the given
		value (from `k`) or to the default, if not in `k`. Does not give
		`errors` if `encoding` can't be found in either `k` or default.
		
		RETURNS A DICT, EDITS `k`
		This method edits the given dict `k`, removing it's `encoding`
		and `errors` keys and returns them in a new dict (with defaults
		applied as needed).
		
		EXPERIMENTAL:
		If encoding keyword is explicitly set to none, both keys are 
		popped and an empty dict is returned; use this in the (probably
		rare) event that you need to ignore default encoding and receive
		bytes. NOTE that this feature takes time and will probably be of
		very little practical use, so it will likely be removed.
		"""
		# EXPERIMENTAL - allow encoding to be overridden to None
		if 'encoding' in k and k['encoding'] == None:
			k.pop('encoding', None)
			k.pop('errors', None)
			return {}
		
		# otherwise, apply defaults
		enc = k.pop('encoding', self.encoding)
		if enc:
			ek = dict(encoding=enc)
			err = k.pop('errors', self.errors)
			if err:
				ek['errors'] = err
			return ek
		return {}
	
	
	# APPLY ENCODING
	def applyEncoding(self, k):
		"""
		Applies defaults to given dict `k`. Removes `errors` value if 
		`encoding` is not set either in `k` or defaults. Does not raise 
		an exception if `encoding` does not exist - just quietly deletes 
		both keys.
		
		DOES NOT RETURN A DICT
		This method doesn't return a dict; it edits the `encoding` and 
		`errors` keys of the given dict `k` leaving other keys untouched.
		
		EXPERIMENTAL:
		If encoding keyword is explicitly set to None, both keys are 
		popped and an empty dict is returned; use this in the (probably
		rare) event that you need to ignore default encoding and receive
		bytes. NOTE that this feature takes time and will probably be of
		very little practical use, so it will likely be removed.
		"""
		# EXPERIMENTAL - allow encoding to be overridden to None
		if 'encoding' in k and k['encoding'] == None:
			k.pop('encoding', None)
			k.pop('errors', None)
			return {}
		
		# otherwise, quietly delete both keys
		enc = k.pop('encoding', None)
		err = k.pop('errors', None)
		
		# reset keys as appropriate
		if enc or self.encoding:
			k['encoding'] = enc or self.encoding
			
			# remove errors if encoding does not exist
			if err and self.errors:
				k['errors'] = err or self.errors





#
# FILE BASE
#
class FileBase(Path, EncodingHelper):
	"""
	Common methods fs.file.File and subclasses will need.
	"""
	def __init__(self, path=None, **k):
		EncodingHelper.__init__(self, **k)
		Path.__init__(self, path, **k)
	
	# SET PATH (or, in this case, forbid setting of path)
	def setpath(self, path):
		"""
		Prevents changing of this file wrappers path. 
		"""
		raise ValueError('fs-immutable-path', xdata())

	# TOUCH
	def touch(self, times=None):
		"""Touch this file."""
		with open(self.path, 'a'):
			os.utime(self.path, times)  
	




#
# STREAM, READER, WRITER
#
class Stream(EncodingHelper):
	
	def __init__(self, stream, **k):
		"""
		Optional `encoding` and `errors` keyword arguments, if specified,
		will cause read data to be decoded.
		"""
		EncodingHelper.__init__(self, **k)
		self.__stream = stream
		
	
	def __del__(self):
		"""Flush and close the contained stream (if open)."""
		try:
			# Don't try to close if self.__stream was never set.
			self.__stream
		except:
			self.__stream = None
		
		# Now we can close without hiding meaningful errors that might be
		# self.__stream being undefined.
		self.close()
	
	
	@property
	def stream(self):
		"""The contained stream."""
		return self.__stream
	
	
	def detach(self):
		"""
		Return a good copy of this stream, nullifying the internal copy.
		"""
		try:
			return self.__stream
		finally:
			self.__stream = None
	
	def close(self):
		"""
		Closes the `self.__stream` stream object. Overriding classes that
		do not work with stream objects should replace this method with
		cleanup suitable to their own non-stream "producer".
		"""
		# don't raise an exception here if the stream was never set
		try:
			self.__stream
		except:
			return
		
		if self.__stream:
			self.__stream.close()
	
	
	def seek(self, *a, **k):
		"""
		Performs seek on the contained stream using any given args and
		kwargs.
		
		NOTE: Not all streams support seek! For example, zip file objects
		      don't seem to have a seek method. You have to account for
		      this manually wherever you use seek.
		"""
		self.__stream.seek(*a, **k)




class Reader(Stream):
	
	def __init__(self, stream, **k):
		"""
		Pass the required `stream` object. If the optional `encoding`
		keyword argument is specified, it will be used to decode the 
		result for readline(), read(), and each value returned by the
		`lines` property.
		"""
		Stream.__init__(self, stream, **k)
		
		# p2/p3
		self.next = self.__next__
	
	
	def __iter__(self):
		"""Line iterator."""
		return self.lines
	
	def __next__(self):
		"""Read and return the next line."""
		return next(self.lines)
	
	
	@property
	def lines(self):
		"""Line generator."""
		k = self.ek
		if k:
			for line in self.stream:
				yield (line.decode(**k))
		else:
			for line in self.stream:
				yield line
	
	
	# READ
	def read(self, *a):
		"""Read any remaining data in the stream."""
		if not self.ek:
			self.read = self.stream.read
		else:
			self.read = self._read
		return self.read(*a)
	
	def _read(self, *a):
		"""Read any remaining data in the stream."""
		return self.stream.read(*a).decode(**self.ek)
		
	
	# READLINE
	def readline(self):
		"""Read the next line. """
		if not self.ek:
			self.readline = self.stream.readline
		else:
			self.readline = self.__next__
		return self.readline()





class Writer(Stream):
	
	# CLOSE
	def close(self):
		"""
		Closes the `self.__stream` stream object. Overriding classes that
		do not work with stream objects should replace this method with
		cleanup suitable to their own non-stream "producer".
		"""
		if self.stream:
			self.flush()
			self.stream.close()
	
	
	# WRITE
	def write(self, data):
		"""Write `data`."""
		if not self.ek:
			self.write = self.stream.write
		else:
			self.write = self._write
		return self.write(data)
	
	def _write(self, data):
		"""Write `data`."""
		return self.stream.write(data.encode(**self.ek))
	
	
	# WRITE LINES
	def writelines(self, datalist):
		"""Write a list of lines, `datalist`."""
		if not self.ek:
			self.writelines = self.stream.writelines
		else:
			self.writelines = self._writelines
		return self.writelines(datalist)
	
	
	def _writelines(self, datalist):
		"""Write a list of lines, `datalist`."""
		for i, v in datalist:
			datalist[i] = v.encode(**self.ek)
		return self.stream.writelines(datalist)
	
	
	# FLUSH
	def flush(self):
		"""Flush the contained stream."""
		if self.stream:
			try:
				self.stream.flush()
			except (ValueError, AttributeError):
				# ignore errors where the stream is already closed (or just
				# doesn't have a 'flush' method).
				pass





#
# EXPERIMENTAL
#



class Buffer(Writer):
	"""
	Buffer's constructor stores any keyword arguments and later (on the
	first call to a write method) uses them to create a StringIO or 
	BytesIO stream where written data will be stored.
	
	When finished writing, use the reader() method to create a Reader 
	that will read from the (detached) buffer stream.
	
	BUFFER IS UNDER CONSTRUCTION!
	 - Still needs some fine-tuning on unicode vs bytes issues. The
	   way StringIO vs BytesIO is selected doesn't account for any
	   encoding specified to the constructor, and that needs to be
	   fixed.
	
	"""
	def __init__(self, **k):
		self.__k = k
		#
		# DO NOT CALL Writer.__init__ HERE!
		#  - Writer.__init__ gets called on first write.
		#
	
	
	def reader(self, **k):
		"""
		This method returns a Reader of the previously written data.
		
		Call reader() only after you've finished writing to the buffer.
		The buffer will no longer be writable after creating a reader
		from it.
		"""
		self.stream.seek(0)
		return Reader(self.detach(), **k)
	
	
	def write(self, data):
		"""Write `data`."""
		
		# The stream is first created based on the type of data given on
		# the first call to write().
		try:
			try:
				# expect unicode...
				strm = Base.create('io.StringIO', type(data)())
			except:
				# accept bytes...
				strm = Base.create('io.BytesIO', type(data)())
		except:
			# Let it work for python versions before 2.6, though apparently
			# this is pretty slow.
			strm = Base.create('StringIO.StringIO')
		
		# Send this stream to Writer so it can be written to;
		# Note that the write method is replaced in Writer in some cases,
		# to speed up future writes to `strm` (and handle any encoding-
		# related tasks!)
		Writer.__init__(self, strm, **self.__k)
		
		# Now write the data; Calling Writer.write both writes the data
		# and replaces the write function so that the _write() method is
		# used for subsequent calls. Buffer subclasses could use this to
		# their advantage.
		return Writer.write(self, data)
	
	
	def writelines(self, datalist):
		"""Write a list of lines, `datalist`."""
		
		# On first call to self.writelines, make sure to write the first
		# line by calling self.write - that way, if the stream will be
		# created (if it hasn't yet).
		self.write(datalist[0])
		
		# use the Writer.writelines method to write any remaining list
		# items (as well as any future calls to writelines).
		if len(datalist) > 1:
			Writer.writelines(self, datalist[1:])
		
		# It's ok if only one line was passed... it will still work, just
		# maybe a little more slowly until multiple lines are sent to 
		# this writelines method.





class ReadCoder(Reader):
	"""
	EXPERIMENTAL!
	
	This class was written to allow CSVReader to work at least somewhat
	usefully across python versions 2/3.
	
	ReadCoder objects read byte or unicode text streams flexibly. The
	CSVReader needs to provide bytes in python 2 and unicode text in
	python 3, so it just trys both and uses whichever works.
	
	The end effect is that row data is given as byte string values in
	python 2 and unicode values in python 3.
	
	For now, that's the best I can achieve. Hopefully the future will
	bring better quality. For now this class (and, so, the CSVReader)
	must remain 'experimental'.
	
	NOTE:
	The name of this class may change. If kept, this class will likely
	move to the fs.__init__ module (or wherever the ever-growing list
	of stream utility objects ends up being placed).
	"""
	
	# INIT
	def __init__(self, stream, **k):
		Reader.__init__(self, stream)
		
		# if you need bytes...
		if 'encode' in k:
			if 'decode' in k:
				raise Exception('conflicting-kwargs', xdata(
						krequire1=['encode','decode']
					))
			
			self.__encoding = k['encode']
			self.__operator = unicode.encode #p2 needs this to be `unicode`
		
		# if you need unicode...
		elif 'decode' in k:
			self.__encoding = k['decode']
			self.__operator = pxbytes.decode #early p2 needs `pxbytes`
		
		else:
			raise Exception('missing-required-kwarg', xdata(
					krequire1=['encode','decode']
				))
		
		self.readline = self.__next__
	
	# LINES
	@property
	def lines(self):
		"""Line generator."""
		try:
			for line in self.stream:
				yield (self.__operator(line, self.__encoding))
		
		# if the above fails, it will fail on the first line, so yield
		# that line, then enter a new loop that doesn't apply encoding
		# or decoding (that is, self.__operator).
		except TypeError:
			yield line
		
		for line in self.stream:
			yield line
			
	# READ
	def read(self, *a):
		try:
			x = self.stream.read(*a)
			return self.__operator(x, self.__encoding)
		except TypeError:
			self.read = self.stream.read
			return x









class Filter(Reader):
	"""
	Filter methods read from a stream and return the result through a
	callable `fn` argument (supplied to the constructor).
	"""
	def __init__(self, stream, fn, *a, **k):
		"""
		Pass `stream` and `fn`, a callable.
		"""
		Reader.__init__(self, stream, **k)
		self.applyEncoding(k)
		self.__fn = fn
		self.__a = a
		self.__k = k
	
	@property
	def lines(self):
		for line in self.stream:
			yield self.__fn(line, *self.__a, **self.__k)
	
	def read(self, *a):
		return self.__fn(self.stream.read(*a), *self.__a, **self.__k)
	
	def readline(self):
		return self.__fn(self.stream.readline(), *self.__a, **self.__k)



"""
BACKUP...
class Filter(Reader):
	def __init__(self, stream, fn, **k):
		Reader.__init__(self, stream, **k)
		self.__fn = fn
	
	@property
	def lines(self):
		for line in self.stream.lines:
			yield self.__fn(line)
	
	def read(self, *a):
		return self.__fn(self.stream.read(*a))
	
	def readline(self):
		return self.__fn(self.stream.readline())
"""
