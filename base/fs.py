"""
Copyright 2015 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

FS - Path, File, Directory.

File and Dir are based on Path. The following apply to all:

 * Setting self.path is relative to the current working directory.
   For all other object methods, given paths that are relative are
   merged with self.path to create an absolute path.
   
 * Creating a File or Dir object requires that the corresponding
   file system object be of the corresponding type if they actuall
   exist. See the Path.expand() keyword description to figure out
   how to make this work for you.
   
 * File and Dir methods that access codecs expect keyword arguments
   for the codecs methods. By default, encoding is set to the value
   of FS_ENCODE (which is originally 'utf-8').
"""

import os, shutil, codecs, glob

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
		self.__p = self.expand(path)
	
	def exists(self, path=None):
		p = self.merge(path)
		return os.path.exists(p)
	
	def getpath(self):
		return self.__p
	
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




class File(Path):
	"""Represents a file."""
	
	def __init__(self, path, **k):
		"""Pass path to file. Keywords apply as to Path.expand()."""
		Path.__init__(self, path, **k)
		if self.exists() and not self.isfile():
			raise ValueError('not-a-file')

	def head(self, lines=12, **k):
		"""Top lines of file. Any kwargs apply to codecs.open()."""
		a = []
		k.setdefault('mode', 'r')
		k.setdefault('encoding', FS_ENCODE)
		with codecs.open(self.path, **k) as fp:
			for i in range(0, lines):
				a.append(fp.readline())
		return ''.join(a)
	
	def read(self, **k):
		"""Read this file. Any kwargs apply to codecs.open()."""
		k.setdefault('mode', 'r')
		k.setdefault('encoding', FS_ENCODE)
		with codecs.open(self.path, **k) as fp:
			return fp.read()
	
	def write(self, data, **k):
		"""Read this file. Any kwargs apply to codecs.open()."""
		k.setdefault('mode', 'w+')
		k.setdefault('encoding', FS_ENCODE)
		with codecs.open(self.path, **k) as fp:
			if not isinstance(data, basestring):
				data = fmt.JFormat().format(data)
			fp.write(data)




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
		Path.__init__(self, path, **k)
		if self.exists() and not self.isdir():
			raise ValueError('not-a-directory')
	
	def cd(self, path):
		"""Change directory the given path."""
		p = self.merge(path)
		if not os.path.isdir(p):
			raise Exception ('not-a-directory')
		self.path = p

	def cp(self, src, dst, **k):
		"""
		Copy src to dst; Kwargs passed to copytree if src is directory.
		"""
		src = self.merge(src)
		if self.exists(dst):
			raise Exception('fs-path-exists', dst)
		if os.path.isdir(src):
			return shutil.copytree(src, self.merge(dst), **k)
		else:
			return shutil.copyfile(src, self.merge(dst))
	
	def ls(self, path=None):
		"""List directory at path."""
		return os.listdir(self.merge(path))
	
	def mkdir(self, path, *a):
		"""Create a directory described by path."""
		os.makedirs(self.merge(path), *a)

	def mv(self, src, dst):
		"""Move src to dst."""
		src = self.merge(src)
		return shutil.move(src, self.merge(dst))
	
	def rm(self, glob=None):
		"""Remove files matching glob pattern."""
		g = self.glob(self.merge(glob))
		for px in g:
			if os.path.isdir(px):
				shutil.rmtree(px)
			else:
				os.remove(px)
	
	# SEARCHING
	def glob(self, path):
		return glob.glob(self.merge(path))
	
	def find(self, glob, path=None):
		p = self.merge(path)
		r = []
		for d, dd, ff in os.walk(p):
			r.extend(self.glob(os.path.join(d, glob)))
		return r
	
	# FILES
	def head(self, path, lines=12, **k):
		"""Return head for existing file at the given path."""
		return File(self.merge(path)).head(lines, **k)
	
	def read(self, path, **k):
		"""Return contents of file at path. Kwargs for codecs.open()."""
		return File(self.merge(path)).read(**k)
	
	def file(self, path, **k):
		"""Return a File object to the given path."""
		return File(self.merge(path), **k)
