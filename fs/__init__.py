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
from . import opener

import os, os.path as ospath



#
# PATH
#  - Base for fs module's classes.
#
class Path(object):
	"""Represents file system paths."""
	
	# INIT
	def __init__(self, path=None, **k):
		"""
		Pass the path this object refers to. Any additional keyword args
		will apply to the Path.expand() method, which is always called on
		this path immediately.
		"""
		self.__p = self.expand(k.get('path', path or '.'), **k)
		self.__n = ospath.normpath(self.__p).split(os.sep)[-1]
	
	
	# STR
	def __str__(self):
		return self.path
	
	# UNICODE
	def __unicode__(self):
		return self.path
	
	
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
		return ospath.exists(self.merge(path))
	
	def getpath(self):
		return self.__p
	
	def setpath(self, path):
		self.__p = path
		self.__n = ospath.normpath(path).split(os.sep)[-1]
	
	def isfile(self, path=None):
		return ospath.isfile(self.merge(path))
	
	def isdir(self, path=None):
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
		"""
		try:
			Path(p).wrapper().touch()
			#wrapper = Path(p).wrapper()
			#print ("WRAPPER! %s" % repr(wrapper))
		except Exception as ex:
			#print ("OPEN! %s" % str(ex))
			with open(p, 'a'):
				os.utime(p, times)
		"""
	
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
		the file there.
		"""
		
		# Files with members will need to create a different kind of
		# object from what gets returned. Pop that key out of kwargs
		# before calling `wrapper`.
		member = Base.kpop(k, 'member')
		
		# now get the file wrapper object and return a reader
		wrapper = self.wrapper(**k)
		
		
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
			raise Exception('no-such-path', {'path' : OP.dirname(path)})
		if v:
			if OP.exists(path):
				if (v=='checkdir') and (not OP.isdir(path)):
					raise Exception('not-a-directory', {'path' : path})
			else:
				if (v=='checkdir'):
					raise Exception('no-such-directory', {'path' : path})
				elif v in ['makepath', 'touch']:
					if not OP.exists(OP.dirname(path)):
						os.makedirs(OP.dirname(path))
					if v == 'touch':
						with open(path, 'a'):
							os.utime(path, None)
				elif (v=='makedirs'):
					os.makedirs(path)
		
		return path





class ImmutablePath(Path):
	"""
	The base for file objects that should not allow their path to
	change.
	"""
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
class Stream(object):
	
	def __init__(self, stream, **k):
		self.__stream = stream
		self.__ek = Base.kcopy(k, 'encoding errors')
	
	def __del__(self):
		try:
			self.close()
		finally:
			self.__stream = None
	
	@property
	def encoding(self):
		"""Encoding specified to constructor."""
		return self.__ek.get('encoding')
	
	@property
	def ek(self):
		"""
		Internal support for subclasses; A dict that provides any given
		`encoding` and/or `errors` values related to encoding/decoding
		read and written stream data. Returns an empty dict if no such
		values were specified to the Stream constructor.
		"""
		return self.__ek
	
	@property
	def stream(self):
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
		if self.__stream:
			self.__stream.close()





class Reader(Stream):
	
	def __init__(self, stream, **k):
		"""
		Pass the required `stream` object. If the optional `encoding`
		keyword argument is specified, it will be used to decode the 
		result for readline(), read(), and each value returned by the
		`lines` property.
		"""
		Stream.__init__(self, stream, **k)
		
		# this should speed things up when encoding is not specified
		if not self.encoding:
			self.read = self.stream.read
			self.readline = self.stream.readline
	
	
	def __iter__(self):
		return self.lines
	
	
	@property
	def lines(self):
		k = self.ek
		if k:
			for line in self.stream:
				yield (line.decode(**k))
		else:
			for line in self.stream:
				yield line
	
	
	def readline(self):
		"""
		Read a line decoding as specified by `encoding` passed to the
		constructor. 
		
		NOTE: If no encoding was specified to the constructor, this 
		      method is replaced by a direct all to the stream's 
		      readline() method.
		"""
		return self.stream.readline().decode(**self.ek)
	
	
	def read(self, *a):
		"""
		Read stream, decoding as specified by `encoding` passed to the
		constructor. 
		
		NOTE: If no encoding was specified to the constructor, this 
		      method is replaced by a direct all to the stream's 
		      readline() method.
		"""
		return self.stream.read(*a).decode(**self.ek)





class Writer(Stream):

	def __init__(self, stream, **k):
		"""
		Pass the required `stream` object.
		
		If the optional `encoding` keyword argument is given, it will be
		used to decode the result for writelines() and write().
		"""
		Stream.__init__(self, stream, **k)
		
		# this should speed things up when encoding is not specified
		k = self.ek
		if not k:
			self.write = self.stream.write
			self.writelines = self.stream.writelines
	
	
	def close(self):
		"""
		Closes the `self.__stream` stream object. Overriding classes that
		do not work with stream objects should replace this method with
		cleanup suitable to their own non-stream "producer".
		"""
		if self.stream:
			self.flush()
			self.stream.close()
	
	#
	# WRITE / WRITE-LINES
	#  - Don't check for k here because if none was passed, this
	#    method will have been replaced in the constructor by a direct
	#    call to the stream's corresponding methods
	#
	def write(self, data):
		return self.stream.write(data.encode(**self.ek))
	
	def writelines(self, datalist):
		return self.stream.writelines(data.encode(**self.ek))
	
	def flush(self):
		"""Flush the contained stream."""
		if self.stream:
			try:
				self.stream.flush
				self.stream.flush()
			except:
				pass





#
# EXPERIMENTAL
#


class Buffer(Writer):
	"""
	Buffer's constructor creates a StringIO or BytesIO stream to store
	all data written to it. When finished writing, call the reader()
	method to receive a Reader that will read from the (detached)
	buffer stream.
	"""
	def __init__(self, **k):
		try:
			try:
				strm = Base.create('io.StringIO')
			except:
				strm = Base.create('io.BytesIO')
		except:
			strm = Base.create('StringIO.StringIO')
		
		# send this stream to Writer so it can be written to
		Writer.__init__(self, strm, **k)
	
	def reader(self):
		self.stream.seek(0)
		return Reader(self.detach())



class Filter(Stream):
	"""
	Filter's various read methods read from a stream and returns the 
	result after passing it through the callable `fn` argument.
	
	Filter implements Reader methods, but need not (and *must* not)
	inherit from Reader because Reader replaces the read and write 
	methods for non-unicode streams with the corresponding method from
	the actual stream it's covering.
	"""
	def __init__(self, stream, fn, **k):
		Stream.__init__(self, stream, **k)
		self.__fn = fn
	
	@property
	def lines(self):
		for line in self.stream.lines:
			yield self.__fn(line)
	
	def read(self, *a):
		return self.__fn(self.stream.read(*a))
	
	def readline(self):
		return self.__fn(self.stream.readline())

