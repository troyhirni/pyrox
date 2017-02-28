"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

TAR - Tar file wrapper.
"""


import tarfile, fnmatch
from .file import *


class Tar(MemberFile):
	"""Tar file support."""
	
	@property
	def names(self):
		"""EXPERIMENTAL"""
		try:
			return self.__names
		except:
			with self.open('r|*') as f:
				self.__names = f.getnames()
			return self.__names
	
	@property
	def members(self):
		"""EXPERIMENTAL"""
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
		EXPERIMENTAL
		
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
		try:
			return tarfile.open(self.path, mode, **k)
		except Exception as ex:
			raise type(ex)('tar-open-fail', xdata(path=self.path, k=k, 
					mode=mode,exists=self.exists(), mime=self.mime.guess
				))
	
	
	# READING
	def read(self, member, **k):
		"""
		Return bytes of the given member.
		"""
		k['member'] = member
		
		# REM: The reader method separates the kwargs (ek from k) and
		#      lets it's read method handle encoding, if specified.
		r = self.reader(**k) 
		return r.read()
	
	
	# WRITE
	def write(self, member, data, mode="w", **k):
		
		# create tarinfo object
		mem = tarfile.TarInfo(member)
		mem.size = len(data)
		
		# always encode to bytes if encoding is provided
		ek = self.extractEncoding(k)
		if ek:
			data = data.encode(**ek)
		
		# create a stream
		try:
			strm = Base.create('io.BytesIO', data)
		except Exception:
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
		ek = self.extractEncoding(k)
		if 'stream' in k:
			return Reader(**ek)
		elif 'member' in k:
			mode = k.get('mode', 'r')
			member = k['member']
			return Reader(self.open(mode).extractfile(member), **ek)
		else:
			raise ValueError('create-reader-fail', xdata( k=k, ek=ek,
				reason='missing-required-arg', requires=['stream','member'],
				detail=self.__class__.__name__
			))
	
	
	# WRITER - Maybe someday... maybe soon :-)
	def writer(self, *a, **k):
		raise NotImplementedError('maybe-someday')



	
	