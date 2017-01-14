"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyro project, distributed under the terms 
of the GNU Affero General Public License.

FS - File System Functionality

The base for pyro file system operations.



"""

from .. import *
from . import opener

import os



def rmkeys(d, rmkeys):
	r = {}
	for k in d:
		if not k in rmkeys:
			r[k]=d[k]
	return r


#
# PATH
#  - Base for fs module's classes.
#
class Path(Base):
	"""Represents file system paths."""
	
	def __init__(self, p=None, **k):
		self.__p = self.expand(k.get('path', p), **k)
	
	def __str__(self):
		return self.path
	
	def __unicode__(self):
		return self.path
	
	@property
	def parent(self):
		return os.path.dirname(self.path)
	
	@property
	def path(self):
		return self.getpath()
	
	@path.setter
	def path(self, path):
		self.setpath(path)
	
	@property
	def opener(self):
		try:
			return self.__opener
		except:
			self.__opener = opener.Opener()
			return self.__opener
	
	"""
	@property
	def dir(self):
		return pyro.create(pyro.importpath("fs.fsdir.Dir"), *a, **k)
	
	@property
	def file(self):
		return pyro.create(pyro.importpath("fs.fsfile.File"), *a, **k)
	"""
	
	def exists(self, path=None):
		return os.path.exists(self.merge(path))
	
	def getpath(self):
		return self.__p
	
	def setpath(self, path):
		self.__p = path
	
	def isfile(self, path=None):
		return os.path.isfile(self.merge(path))
	
	def isdir(self, path=None):
		return os.path.isdir(self.merge(path))
	
	def islink(self, path=None):
		"""True if path is a symbolic link."""
		return os.path.islink(self.merge(path))
	
	def ismount(self, path=None):
		"""True if path is a mount point."""
		return os.path.ismount(self.merge(path))
	
	def touch(self, path=None, times=None):
		"""Touch file at path. Arg times applies to os.utime()."""
		p = self.merge(path)
		with open(p, 'a'):
			os.utime(p, times)  
	
	def merge(self, path):
		"""Returns the given path relative to self.path."""
		if not path:
			return self.path
		p = os.path.expanduser(path)
		if os.path.isabs(p):
			return os.path.normpath(p)
		else:
			p = os.path.join(self.path, p)
			return os.path.abspath(os.path.normpath(p))
	
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
			return open(self.path, mode, **k)
		
		# text
		else:
			k.setdefault('encoding', DEF_ENCODE)
			return self.opener.open(self.path, mode, **k)
	
	
	
	# READER
	def reader(self, mode="r", **k):
		"""Open file at self.path and return a Reader."""
		return Reader(self.open(mode, **k))
	
	# WRITER
	def writer(self, mode="w", **k):
		"""Open file at self.path and return a Writer."""
		return Writer(self.open(mode, **k))
	
	@classmethod
	def expand(cls, path=None, **k):
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
	def setpath(self, path):
		raise ValueError('fs-immutable-path', xdata())





#
# STREAM, READER, WRITER
#
class Stream(object):
	def __init__(self, stream):
		self.__stream = stream
	
	def __del__(self):
		try:
			self.close()
		finally:
			self.__stream = None
	
	@property
	def stream(self):
		return self.__stream
	
	def close(self):
		self.__stream.close()



class Reader(Stream):
	def read(self, *a):
		return self.stream.read(*a)



class Writer(Stream):
	def write(self, data):
		return self.stream.write(data)

