"""
Copyright 2014-2017 Troy Hirni
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
		"""
		Pass an optional file system path. Default is '.'. Kwargs apply 
		as to Path.expand().
		"""
		p = k.get('dir', path)
		if not 'affirm' in k:
			k['affirm'] = 'checkdir'
		try:
			Path.__init__(self, p, **k)
		except Exception:
			raise ValueError('fs-invalid-dir', xdata(path=p)) 
		
		# bypassing more pythonic shenanigans
		try:
			self.walk = os.walk
		except:
			self.walk = os.path.walk
	
	
	# CALL - EXPERIMENTAL
	def __call__(self, item):
		"""
		Calling a Path object as a function returns a new Path object that
		points to its path "merged" with the (required) given `item`.
		
		For `Dir` objects, the given `item` may also be the integer offset
		into the directory listing.
		"""
		try:
			# this works if item is an integer index into this directory
			return Path.__call__(self, self[item])
		except TypeError:
			# this works if item is a string path
			return Path.__call__(self, item)
	
	
	def __getitem__(self, key):
		"""
		Dir objects can act as lists of the full path to the items inside
		the directory to which they point; Dir()[0] returns the full path
		to the first item in its directory listing.
		"""
		ls = self.ls()
		return self.merge(ls[key])
	
	
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
	
	#
	# Single file operations, path relative to this directory.
	#
	
	def head(self, path, lines=12, **k):
		"""Return head for existing file at the given path."""
		
		# get the path to `path` relative to this directory
		p = Path(self.merge(path))
		
		# get a reader for that file
		r = p.reader(**k)
		
		# iterate, collecting `head` results
		rr = []
		for line in r.lines:
			rr.append(line.strip())
			lines -= 1
			if lines < 1:
				break
		return rr
		#return self.file(path).head(lines, **k)
	
	def read(self, path, **k):
		"""Return contents of file at path."""
		return self.file(path).read(**k)
	
	def file(self, path, **k):
		"""Return a File object to the given path."""
		return Base.ncreate('fs.file.File', self.merge(path), **k)
	
	
	#
	# Directory contents actions
	#
	
	def cp(self, pattern, dst, **k):
		"""
		Copy src to dst; If src is directory, any keyword arguments are 
		passed to shutil.copytree().
		"""
		try:
			for src in self.match(pattern):
				#print (src)
				curDest = self.merge(dst)
				if os.path.isdir(src):
					shutil.copytree(src, curDest, **k)
				else:
					shutil.copy(src, curDest)
		except Exception as ex:
			raise type(ex)('copy-fail', xdata(
				src=src, dst=curDest, err=ex.args
			))
		"""HOLD ON TO THIS A SEC...
		for src in self.match(pattern):
			if self.exists(dst):
				raise Exception('fs-path-exists',  xdata(dest=dst))
			if os.path.isdir(src):
				return shutil.copytree(src, self.merge(dst), **k)
			else:
				return shutil.copyfile(src, self.merge(dst))
		"""
	
	def mkdir(self, path, *a):
		"""
		Create a directory described by path. If appended, additional 
		argument (mode) is passed on to os.makedirs().
		"""
		os.makedirs(self.merge(path), *a)

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
	
	
	#
	# Pattern Searching - Match, Find
	#
	
	def match(self, pattern):
		"""Return matching directory items for the given pattern."""
		return glob.glob(self.merge(pattern))
	
	
	def search(self, path, pattern=None, **k):
		"""
		Search directories recursively starting at the given `path`; 
		return list of all paths unless argument `pattern` is specified.
		
		KEYWORD ARGUMENT:
		 * If `fn` keyword is specified, its value must be callable; this 
		   callable will be called once for each result path. If args 
		   keyword exists, it must be an array of values to be passed as 
		   individual additional arguments to fn.
		
		   WARNING: There is no 'confirm' or 'undo' when passing a 'fn'.     
						    ALWAYS CHECK the find results *without a function* 
						    BEFORE using it with a function.
		"""
		if not pattern:
			raise ValueError('fs-pattern-required', xdata())
		path = self.merge(path)
		rlist = []
		for d, dd, ff in self.walk(path):
			rlist.extend(self.match(os.path.join(d, pattern)))
		if 'fn' in k:
			fn = k['fn']
			for fpath in rlist:
				rr = {}
				aa = k.get('args', [])
				fn(fpath, *aa)
		else:
			return rlist
	
	
	def find(self, pattern, **k):
		"""
		Calls the .search() method passing this object's path and the 
		given `pattern` and keyword args. Read the search method help for
		more information.
		
		NOTE ESPECIALLY the warning concerning the `fn` keyword argument.
		"""
		return self.search(self.path, pattern, **k)

