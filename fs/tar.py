"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

TAR - Covers tar files.

The Tar class is currently read-only.
"""

import tarfile, fnmatch
from .bfile import *


class Tar(ByteFile):
	"""Tar file support."""
	
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
	def write(self, member, data, mode="a", **k):
		
		# create tarinfo object
		mem = tarfile.TarInfo(member)
		mem.size = len(data)
		
		ek = self.extractEncoding(k)
		if ek:
			# always encode to bytes if encoding is provided
			data = data.encode(**ek)
		
		# create a stream
		try:
			try:
				# This is a tar file, so it should be bytes...
				#print (1)
				strm = Base.create('io.BytesIO', data)
				#print (2)
			except:
				
				#
				# ...but in python 2, it might be thought of as a string
				# even if it's really bytes. 
				# 
				# CHECK THIS!
				#
				# TO-DO: Look into this further; this might not be necessary 
				# (or if it is, might not be the best solution).
				#
				
				#print (3)
				strm = Base.create('io.StringIO', data)
				#print (4)
				
		except ImportError:
			# for early python 2
			#print (5)
			strm = Base.create('cStringIO.StringIO', data)
			#print (6)
		
		
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



	
	