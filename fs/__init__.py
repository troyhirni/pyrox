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
	
	#  --- UNDER CONSTRUCTION ---
	
	#
	# WRAPPER
	#
	def wrapper(self, **k):
		"""
		Returns a fs.File-based object wrapping the fs object at this
		pasth. The default for files whose mime type can't be matched 
		here is fs.file.File.
		"""
		mm = self.mime
		if self.isdir() or self.ismount():
			raise Exception('open-fail', xdata(
				path=self.path, reason='file-required', k=k
			))
		
		# APPLICATION
		if mm.type == 'application':
			
			# tar, tar.bz2, tar.gz, tgz
			if mm.subtype == 'x-tar':
				return Base.ncreate('fs.tar.Tar', self.path, **k)
			
			# zip
			elif mm.subtype == 'zip':
				return Base.ncreate('fs.zip.Zip', self.path, **k)
			
			elif mm.subtype == 'json':
				tj = Base.ncreate('data.transform.TransformJson')
				return Base.ncreate(
					'fs.tfile.TransformFile', tj, self.path, **k
				)
		
		# TEXT/ENC 
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
		
		# DEFAULT - for plain text or, as a default, any kind of file
		return Base.ncreate('fs.file.File', self.path, **k)
	
	
	
	
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
		#'print ("wrapper %s" % repr(wrapper))
		
		
		# -- CONTAINER WRAPPER HANDLING (TAR/ZIP) --
		
		# check for member
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
			
			#
			# CAN (SOMETHING LIKE) THIS BE MADE TO WORK?
			#  - Call reader, which in turn will call wrapper to get a file
			#    wrapper covering the given `member`...
			#  - If it's a tar or zip wrapper, it will wind up right here
			#    again and call reader again recursively. 
			#  - Eventually, we'll end up at a member that doesn't contain
			#    a tar/zip file, and the reader will be returned from
			#    the code below.
			#
			# mwrap = mpath.reader(member=member)
			#
			# I just don't see how to make the stream come out right.
			# Maybe a special StreamWrapper class that chains the reads
			# from the final stream back through previous Stream objects
			# until the reads end up where they should?
			#
			
			# Return the resulting wrapper's Reader, created with
			# this wrapper's stream. (Detatch nullifies it's own copy of
			# the stream and returns a live copy.)
			ownerstream = wrapper.reader(member=member).detatch()
			
			#print ("mwrap %s" % repr(mwrap))
			return mwrap.reader(stream=ownerstream)
		
		
		
		# -- NON-CONTANER HANDLING --
		return wrapper.reader()




	#
	# --- EXISTING METHODS ---
	#
	
	
	# INIT
	def __init__(self, path=None, **k):
		"""
		Pass the path this object refers to. Any additional keyword args
		will apply to the Path.expand() method, which is always called on
		this path immediately.
		"""
		self.__p = self.expand(k.get('path', path), **k)
	
	
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
	
	def __del__(self):
		try:
			self.close()
		finally:
			self.__stream = None
	
	@property
	def stream(self):
		return self.__stream
	
	def detatch(self):
		"""
		Return a good copy of this stream, nullifying the internal copy.
		"""
		try:
			return self.__stream
		finally:
			self.__stream = None
	
	
	def close(self):
		if self.__stream:
			self.__stream.close()
	
	def __init__(self, stream):
		self.__stream = stream





class Reader(Stream):
		
	def __iter__(self):
		return self.lines
	
	@property
	def lines(self):
		for line in self.stream:
			yield line

	def read(self, *a):
		return self.stream.read(*a)
	
	def readline(self):
		return self.stream.readline()





class Writer(Stream):
	
	def write(self, data, *a, **k):
		return self.stream.write(data)
	
	def writeline(self, data):
		return self.stream.writeline(data)





