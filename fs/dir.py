"""
Copyright 2014-2016 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

DIR - Directory

WARNING: Dir methods that accept a 'pattern' argument perform their
				 operations on all matching files and directories. Be very 
				 careful with this. There's neither confirmation nor "undo"!

All classes are based on fs.Path:
	 
 * Creating a File or Dir object requires that the specified path
	 or directory actually exist. See the fs.Path.expand() keyword 
	 description to figure out how to make this work for you.
	 
 * File and Dir methods that access codecs expect keyword arguments
	 for the codecs methods. By default, encoding is set to the value
	 of DEF_ENCODE (which is originally 'utf-8'). For files, use the
	 mode keyword with 'w', 'r', 'wb', etc... The mode determines 
	 whether files are read/written with codecs or just plain bytes.
"""

from . import *

import os, shutil, glob

class Dir(Path):
	"""
	Directory functions. Any partial paths given as arguments to 
	methods will be taken as relative to self.path. Setting self.path
	with a relative path will be taken as relative to the current
	working directory.
	
	Setting self.path is relative to the current working directory.
	For all other object methods, given paths that are relative are
	merged with self.path to create an absolute path relative to the
	current path.
	"""
	
	def __init__(self, path=None, **k):
		"""Pass a file system path. Kwargs apply as to Path.expand()."""
		p = k.get('dir', path)
		if not 'affirm' in k:
			k['affirm'] = 'checkdir'
		try:
			Path.__init__(self, p, **k)
		except Exception:
			raise ValueError('fs-invalid-dir', xdata(path=p)) 
	
	# Path-only methods
	def cd(self, path):
		"""Change directory the given path."""
		p = self.merge(path)
		if not os.path.isdir(p):
			raise Exception ('fs-not-a-dir', xdata(path=p))
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
		return self.file(path).head(lines, **k)
	
	def read(self, path, **k):
		"""Return contents of file at path."""
		return self.file(path).read(**k)
	
	def file(self, path, **k):
		"""Return a File object to the given path."""
		return ncreate('fs.file.File', self.merge(path), **k)
	
	# Pattern-Matching Methods
	def cp(self, pattern, dst, **k):
		"""
		Copy src to dst; If src is directory, any keyword arguments are 
		passed to shutil.copytree().
		"""
		for src in self.match(pattern):
			if self.exists(dst):
				raise Exception('fs-path-exists',  xdata(dest=dst))
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
			raise ValueError('fs-pattern-required', xdata())
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


