"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

TAR - Covers tar files.

The Tar class is currently read-only.
"""

import tarfile, fnmatch
from .file import *


class Tar(ByteFile):
	"""Tar file support."""
	
	def __init__(self, path, mode='r', **k):
		File.__init__(self, path, **k)
		if 'encoding' in k:
			self.__encoding = k['encoding']
	
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
	
	
	
	def memberinfo(self):
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
					try:
						rr[m.name] = dict(
							name = m.name,
							size = m.size,
							mtime = m.mtime,
							mode = m.mode,
							type = m.type,
							linkname = m.linkname,
							uid = m.uid,
							gid = m.gid,
							uname = m.uname,
							gname = m.gname #,pax = m.pax_headers	
						)
					except:
						raise
						
			self.__meminfo = rr
			return rr

	
	# OPEN TAR FILE
	def open(self, mode="r", **k):
		"""Open the tarfile; return the TarFile object."""
		return tarfile.open(self.path, mode, **k)
	
	
	# READING
	def read(self, member, **k):
		k['member'] = member
		if self.__encoding:
			k.setdefault(self.__encoding)
		r = self.reader(**k)
		return r.read()
	
	
	# WRITE
	def write(self, member, data, mode="a", **k):
		
		# create tarinfo object
		mem = tarfile.TarInfo(member)
		mem.size = len(data)
		
		if self.__encoding:
			k.setdefault('encoding', self.__encoding)
		
		if 'encoding' in k:
			data=data.encode(k['encoding'])
		
		# create a stream
		try:
			try:
				# This is a tar file, so it should be bytes...
				strm = Base.create('io.BytesIO', data)
			except:
				# ...but in python 2, it might be thought of as a string
				# even if it's really bytes. 
				# 
				# TO-DO: Look into this further; this might not be necessary 
				# (or if it is, might not be the best solution).
				strm = Base.create('io.StringIO', data)
		except ImportError:
			# for early python 2
			strm = Base.create('cStringIO.StringIO', data)
		
		# add the member
		with self.open(mode) as fp:
			fp.addfile(mem, strm)
	
	
	# READER
	def reader(self, **k):
		"""
		Return a `Reader` object for `member`. If reading unicode, an 
		`encoding` keyword must be specified so that the data can be 
		decoded to unicode.
		"""
		if self.__encoding:
			k.setdefault('encoding', self.__encoding)
		if 'stream' in k:
			return Reader(k) # pass k, NOT k['stream']!
		elif 'member' in k:
			mode = k.get('mode', 'r')
			member = k['member']
			return Reader(self.open(mode).extractfile(member), **k)
		else:
			raise ValueError('create-reader-fail', xdata( k=k,
				reason='missing-required-arg', requires=['stream','member'],
				detail=self.__class__.__name__
			))
	
	
	# WRITER - Maybe someday... maybe soon :-)
	def writer(self, *a, **k):
		raise NotImplementedError('maybe-someday')



	
	