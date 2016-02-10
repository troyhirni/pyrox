"""
Copyright 2014-2016 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

FS - Path, File, Directory.

WARNING: Dir methods that accept a 'pattern' argument perform their
				 operations on all matching files and directories. Be very 
				 careful with this. There's neither confirmation nor "undo"!

All classes are based on base.Path:

 * Setting self.path is relative to the current working directory.
	 For all other object methods, given paths that are relative are
	 merged with self.path to create an absolute path relative to the
	 current path.
	 
 * Creating a File or Dir object requires that the specified path
	 or directory actually exist. See the base.Path.expand(). keyword 
	 description to figure out how to make this work for you.
	 
 * File and Dir methods that access codecs expect keyword arguments
	 for the codecs methods. By default, encoding is set to the value
	 of FS_ENCODE (which is originally 'utf-8'). For files, use the
	 mode keyword with 'w', 'r', 'wb', etc... The mode determines 
	 whether files are read/written with codecs or just plain bytes.
"""

import os, shutil, glob, gzip, zipfile, json, ast, tarfile

try:
	from ..base import *
except:
	from base import *





class Dir(Path): #base.Path
	"""
	Directory functions. Any partial paths given as arguments to 
	methods will be taken as relative to self.path. Setting self.path
	with a relative path will be taken as relative to the current
	working directory.
	"""
	
	def __init__(self, path=None, **k):
		"""
		Pass path to a directory. Kwargs apply as to base.Path.expand().
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
	
	# Pattern-Matching Methods
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
		"""Pass path to file. Keywords apply as to base.Path.expand()."""
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
	
	# READ
	def read(self, mode='r', **k):
		"""Open and read file at self.path. Default mode is 'r'."""
		with self.open(mode, **k) as fp:
			return fp.read()
	
	# WRITE
	def write(self, data, mode='w', **k):
		"""Open and write data to file at self.path."""
		with self.open(mode, **k) as fp:
			fp.write(data)
	
	# TOUCH
	def touch(self, times=None):
		"""Touch this file."""
		with open(self.path, 'a'):
			os.utime(self.path, times)  





class Gzip(File):
	"""Gzip file support; EXPERIMENTAL."""
	def open(self, mode='rb', **k):
		return gzip.open(self.path, mode, **k)





class Tar(File):
	"""Tar file support; EXPERIMENTAL."""
	
	# OPEN TAR FILE
	def open(self, mode="r", **k):
		"""Open the tarfile; return the TarFile object."""
		return tarfile.open(self.path, mode="r", **k)
	
	def ls(self):
		return self.names
	
	@property
	def names(self):
		try:
			return self.__names
		except:
			with self.open('r|*') as f:
				self.__names = f.getnames()
			return self.__names

	@property
	def members(self):
		try:
			return self.__members
		except:
			rr = {}
			with self.open('r|*') as f:
				mm = f.getmembers()
				for m in mm:
					rr[m.name] = m
			self.__members = rr
			return rr
	
	def memberinfo(self, name):
		"""
		Return with member names as keys; each value is a dict containing
		information on the corresponding member.
		"""
		try:
			return self.__meminfo
		except:
			rr = {}
			with self.open('r|*') as f:
				mm = f.getmembers()
				for m in mm:
					rr[name] = dict(
						size = m.size,
						mtime = m.mtime,
						mode = m.mode,
						type = m.type,
						linkname = m.linkname,
						uid = m.uid,
						gid = m.gid,
						uname = m.uname,
						gname = m.gname,
						pax = m.pax_headers	
					)
			self.__meminfo = rr
			return rr
	
	def read(self, member, mode='r'):
		return self.reader(member, mode).read()
	
	def reader(self, member, mode='r'):
		return Reader(self.open(mode).extractfile(member))
	
	def writer(self, *a):
		raise NotImplementedError()
	
	def write(self, *a):
		raise NotImplementedError()





class Zip(File):
	"""Zip file."""
	
	def __init__(self, path, **k):
		"""Pass path to file. Keywords apply as to base.Path.expand()."""
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

