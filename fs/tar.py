"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

TAR - Covers tar files.

The Tar class is currently read-only.
"""

import tarfile, fnmatch
from .file import *


class Tar(File):
	"""Tar file support; EXPERIMENTAL."""
	
	def __init__(self, path, mode='r', **k):
		File.__init__(self, path, **k)
		self.__innerdir = '/' #X
	
	@property
	def names(self):
		try:
			return self.__names
		except:
			self.__loadnames()
			return self.__names
	
	def __loadnames(self):
		with self.open('r|*') as f:
			self.__names = f.getnames()

	@property
	def members(self):
		try:
			return self.__members
		except:
			self.__loadmembers()
			return self.__members
	
	def __loadmembers(self):
		rr = {}
		with self.open('r|*') as f:
			mm = f.getmembers()
			for m in mm:
				rr[m.name] = m
		self.__members = rr
	
	def memberinfo(self, name):
		"""
		Return a dict with member names as keys; each value is a dict 
		containing information on the corresponding member.
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

	
	# OPEN TAR FILE
	def open(self, mode="r", **k):
		"""Open the tarfile; return the TarFile object."""
		return tarfile.open(self.path, mode, **k)
	
	
	# FILE-LIKE
	def reader(self, **k):
		"""Read and return a reader for `member`."""
		if 'stream' in k:
			return Reader(k) # pass k, NOT k['stream']!
		elif 'member' in k:
			mode = k.get('mode', 'r')
			member = k['member']
			return Reader(self.open(mode).extractfile(member))
		else:
			raise ValueError('create-reader-fail', xdata( k=k,
				reason='missing-required-arg', requires=['stream','member'],
				detail=self.__class__.__name__
			))
	
	#
	# TO DO: figure out how to implement this!
	#
	def write(self, *a, **k):
		raise NotImplementedError()
	
	def writer(self, *a, **k):
		raise NotImplementedError()
	
	
	
	"""
	#
	# EXPERIMENTAL
	#
	"""
	
	# FILTER - glob-like pattern matching of member names
	def filter(self, pattern):
		"""
		Glob-like pattern matching of member names. Eg, *.txt, etc...
		"""
		return fnmatch.filter(self.names, pattern)

