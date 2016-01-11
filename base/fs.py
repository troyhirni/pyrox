"""
Copyright 2015 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

FS - Path, File, Directory.

WARNING: Dir methods that accept a 'pattern' argument perform their
				 operations on all matching files and directories. Be very 
				 careful with this. There's neither confirmation nor "undo"!

File, Zip, and Dir are based on Path. The following apply to all:

 * Setting self.path is relative to the current working directory.
	 For all other object methods, given paths that are relative are
	 merged with self.path to create an absolute path relative to the
	 current path.
	 
 * Creating a File or Dir object requires that the specified path
	 or directory actually exist. See the Path.expand() keyword 
	 description to figure out how to make this work for you.
	 
 * File and Dir methods that access codecs expect keyword arguments
	 for the codecs methods. By default, encoding is set to the value
	 of FS_ENCODE (which is originally 'utf-8'). For files, use the
	 mode keyword with 'w', 'r', 'wb', etc... The mode determines 
	 whether files are read/written with codecs or just plain bytes.
"""

import os, shutil, codecs, glob, zipfile

try:
	from ..base import *
except:
	from base import *

from . import fmt


FS_ENCODE = DEF_ENCODE



class Path(object):
	"""Represents file system paths."""
	
	def __init__(self, p=None, **k):
		self.__p = self.expand(k.get('path', p), **k)
	
	def __str__(self):
		return self.path
	
	def __unicode__(self):
		return self.path
	
	@property
	def path(self):
		return self.getpath()
	
	@path.setter
	def path(self, path):
		self.setpath(path)
	
	def exists(self, path=None):
		p = self.merge(path)
		return os.path.exists(p)
	
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
			raise Exception('no-such-path', {'path' : path})
		if v and (not OP.exists(path)):
			if (v=='checkdir'):
				raise Exception('no-such-dir', {'path' : path})
			elif v in ['makepath', 'touch']:
				if not OP.exists(OP.dirname(path)):
					os.makedirs(OP.dirname(path))
				if v == 'touch':
					with open(path, 'a'):
						os.utime(path, None)
			elif (v=='makedirs'):
				os.makedirs(path)
		
		return path





class Dir(Path):
	"""
	Directory functions. Any partial paths given as arguments to 
	methods will be taken as relative to self.path. Setting self.path
	with a relative path will be taken as relative to the current
	working directory.
	"""
	
	def __init__(self, path=None, **k):
		"""
		Pass path to a directory. Keywords apply as to Path.expand().
		"""
		Path.__init__(self, k.get('dir', path), **k)
		if self.exists() and not self.isdir():
			raise ValueError('not-a-directory')
	
	# Path-only methods
	def cd(self, path):
		"""Change directory the given path."""
		p = self.merge(path)
		if not os.path.isdir(p):
			raise Exception ('not-a-directory')
		self.path = p
	
	def ls(self, path=None):
		"""List directory at path."""
		return os.listdir(self.merge(path))
	
	def mkdir(self, path, *a):
		"""
		Create a directory described by path. If appended, additional 
		argument (mode) is passed on to os.makedirs().
		"""
		os.makedirs(self.merge(path), *a)
	
	
	# Single file operations, path relative to this directory.
	def head(self, path, lines=12, **k):
		"""Return head for existing file at the given path."""
		return File(self.merge(path)).head(lines, **k)
	
	def read(self, path, **k):
		"""Return contents of file at path."""
		return File(self.merge(path)).read(**k)
	
	def file(self, path, **k):
		"""Return a File object to the given path."""
		return File(self.merge(path), **k)
	
	
	#
	# Pattern-Matching Methods
	#
	def cp(self, pattern, dst, **k):
		"""
		Copy src to dst; If src is directory, any keyword arguments are 
		passed to shutil.copytree().
		"""
		for src in self.match(pattern):
			if self.exists(dst):
				raise Exception('fs-path-exists', dst)
			if os.path.isdir(src):
				return shutil.copytree(src, self.merge(dst), **k)
			else:
				return shutil.copyfile(src, self.merge(dst))

	def mv(self, pattern, dst):
		"""Move pattern matches to dst."""
		for src in self.match(pattern):
			shutil.move(src, self.merge(dst))
	
	def rm(self, pattern):
		"""Remove files matching pattern."""
		for px in self.match(pattern):
			if os.path.isdir(px):
				shutil.rmtree(px)
			else:
				os.remove(px)
	
	
	# Pattern Searching - Match, Find
	def match(self, pattern):
		"""
		Return matching directory items for the given pattern.
		"""
		return glob.glob(self.merge(pattern))
		
	
	def find(self, path=".", pattern=None, **k):
		"""
		Walk through directories recursively, starting at path; return 
		list of full paths matching pattern.
		
		Path is optional and defaults to the current directory specified 
		for this Dir object. Pattern is required, but may be set by name.
		For example: d.find(pattern="*.pyc")
		
		If fn keyword is specified, its value must be callable; it will 
		be called once for each result path. If args keyword exists, it
		must be an array of values to be passed as individual additional
		arguments to fn.
		
		WARNING: There is no 'confirm' or 'undo' when passing a 'fn'.     
						 Always check the find results without a function BEFORE
						 using it with a function.
		"""
		if not pattern:
			raise ValueError('fs-pattern-required')
		path = self.merge(path)
		rlist = []
		for d, dd, ff in os.walk(path):
			rlist.extend(self.match(os.path.join(d, pattern)))
		if 'fn' in k:
			fn = k['fn']
			for fpath in rlist:
				aa = k.get('args', [])
				fn(fpath, *aa)
		else:
			return rlist




class ImmutablePath(Path):
	def setpath(self, path):
		raise ValueError('fs-immutable-path')



class File(ImmutablePath):
	"""Represents a file."""
	
	def __init__(self, path, **k):
		"""Pass path to file. Keywords apply as to Path.expand()."""
		Path.__init__(self, k.get('file', path), **k)
		if self.exists() and not self.isfile():
			raise ValueError('not-a-file')
	
	# HEAD
	def head(self, lines=12, **k):
		"""Top lines of file. Any kwargs apply to codecs.open()."""
		a = []
		k.setdefault('mode', 'r')
		k.setdefault('encoding', FS_ENCODE)
		with self.open(**k) as fp:
			for i in range(0, lines):
				a.append(fp.readline())
		return ''.join(a)
	
	# OPEN
	def open(self, **k):
		"""
		Open file at self.path with codecs.open(), or with the built-in
		open method if mode includes a 'b'. All kwargs are passed for 
		option, either so use only those that are appropriate to the 
		required mode.
		
		Returns the open file pointer.
		
		IMPORTANT: 
		 * To read binary data: theFile.read(mode="rb")
		 * To read unicode text: theFile.read(encoding="<encoding>")
		 * To write binary data: theFile.write(theBytes, mode="wb")
		 * To write unicode text: theFile.write(s, encoding="<encoding>")
		
		With mode "r" or "w", codecs automatically read/write the BOM
		where appropriate (assuming you specify the right encoding). 
		However, if you have text to save as encoded bytes, you can 
		do this so as to save BOM and bytes as encoded:
			>>> theFile.write(theBytes, mode="wb")
		
		This insures that byte string (already encoded) are written 
		"as-is", including the BOM if any, and can be read by:
			>>> s = theFile.read(encoding="<encoding>")
		"""
		k.setdefault('mode', 'rw+')
		if 'b' in k['mode']:
			return open(self.path, **k)
		else:
			k.setdefault('encoding', FS_ENCODE)
			return codecs.open(self.path, **k)
	
	# READ
	def read(self, **k):
		"""Open and read file at self.path. Default mode is 'r'."""
		k.setdefault('mode', 'r')
		with self.open(**k) as fp:
			return fp.read()
	
	# WRITE
	def write(self, data, **k):
		"""Open and write data to file at self.path."""
		k.setdefault('mode', 'w')
		with self.open(**k) as fp:
			fp.write(data)
	
	# TOUCH
	def touch(self, times=None):
		"""Touch this file."""
		with open(self.path, 'a'):
			os.utime(self.path, times)  




class Zip(File):
	"""Zip file."""
	
	def __init__(self, path, **k):
		"""Pass path to file. Keywords apply as to Path.expand()."""
		Path.__init__(self, k.get('zip', path), **k)
		with zipfile.ZipFile(self.path, 'w') as z:
			pass
	
	def namelist(self):
		with zipfile.ZipFile(self.path, 'r') as z:
			return z.namelist()
	
	def read(self, zpath):
		with zipfile.ZipFile(self.path, 'r') as z:
			return z.read(zpath)
	
	def write(self, zpath, data):
		with zipfile.ZipFile(self.path, 'a') as z:
			z.writestr(zpath, data)

