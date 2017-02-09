"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyro project, distributed under
the terms of the GNU Affero General Public License.

ZIP - Covers zip files.

Use the Zip class to read, write, and open streams for reading. I'm
still working on how to write, but for now - sorry - you still have
to write all in one big block - no stream writing yet. Hopefully
someday, though.
"""


import zipfile
from .file import *


class Zip(File):
	"""
	Read and write .zip files.
	
	Zip file works differently from other File-based classes in that 
	its open method is not available for reading unziped data from the
	file.
	"""
	
	def __init__(self, path, pwd=None, comp=None, b64=None, **k):
		"""
		Pass path to file. Other optional arguments are:
		 * pwd - a password
		 * comp - compression: either ZIP_DEFLATED or default ZIP_STORED
		 * b64 - allowZip64: allow zipfile size > 2GB
		
		Keywords apply as to base.Path.expand().
		"""
		File.__init__(self, k.get('zip', path), **k)
		
		# store password
		self.__pass = pwd
		self.__comp = comp if comp else zipfile.ZIP_DEFLATED
		self.__b64 = b64
		
		# force creation of the file
		with self.open(mode='a') as z:
			z.close()
	
	@property
	def names(self):
		"""This file's `member` names."""
		return self.namelist()
	
	
	# OPEN
	def open(self, mode='r', **k):
		"""Returns a ZipFile object."""
		try:
			return zipfile.ZipFile(self.path, mode, self.__comp, self.__b64)
		except RuntimeError:
			try:
				self.__comp = zipfile.ZIP_DEFLATED
				return zipfile.ZipFile(self.path, mode, self.__comp, self.__b64)
			except:
				self.__comp = zipfile.ZIP_STORED
				return zipfile.ZipFile(self.path, mode, self.__comp, self.__b64)
	
	# TEST
	def test(self):
		with self.open() as z:
			try:
				return z.testzip()
			finally:
				z.close()
	
	
	# NAME LIST
	def namelist(self):
		"""This file's `member` names."""
		with self.open() as z:
			try:
				return z.namelist()
			finally:
				z.close()
	
	
	# INFO LIST
	def infolist(self):
		with self.open() as z:
			try:
				return z.infolist()
			finally:
				z.close()
	
	
	# READ
	def read(self, member, **k):
		"""
		Read `member`.
		
		Argument `member` is required, to specify which member to read.
		
		If optional keyword arg `mode` is specified, it replaces the 
		default read mode 'r'.
		
		If optional kwarg `pwd` is specified, it's applied.
		
		If optional kwarg 'encoding' is supplied, result is decoded after
		being read. Optional kwarg 'errors' is also applied if given.
		"""
		ek = Base.kcopy(k, 'encoding errors')
		rk = Base.kcopy(k, 'mode pwd')
		rk.setdefault('mode', 'r')
		with self.open() as z:
			try:
				if 'encoding' in ek:
					return z.read(member, **rk).decode(**ek)
				else:
					return z.read(member, **rk)
			finally:
				z.close()
	
	
	# WRITE
	def write(self, member, data, mode='a', **k):
		"""
		Write data to member (zip path) within the zip file. Default mode
		is 'a'. (To overwrite all contents, use mode='w'.)
		
		If optional keyword arg 'encoding' is supplied, data is encoded
		before being written.
		"""
		ek = Base.kcopy(k, 'encoding errors')
		rk = Base.kcopy(k, 'mode pwd')
		with self.open(mode, **k) as z:
			try:
				if 'encoding' in ek:
					z.writestr(member, data.encode(**ek), **rk)
				else:
					z.writestr(member, data, **rk)
			finally:
				z.close()
	
	
	# READER
	def reader(self, **k):
		"""
		Returns a Reader for the member specified member (or stream). All
		args are given by keyword.
		"""
		if 'stream' in k:
			return Reader(k['stream'])
		elif 'member' in k:
			member = Base.kpop(k, 'member')
			mode = Base.kpop(k, 'mode') or 'r'
			pwd = Base.kpop(k, 'pwd')
			with self.open() as z:
				return Reader(z.open(member, mode, pwd), **k)
		else:
			raise ValueError('create-reader-fail', xdata( k=k,
				reason='missing-required-arg', requires=['stream','member'],
				detail=self.__class__.__name__
			))
	
	
	# WRITER
	def writer(self, **k):
		raise NotImplementedError('maybe-someday')
		








