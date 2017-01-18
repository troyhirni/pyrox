"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyro project, distributed under
the terms of the GNU Affero General Public License.

ZIP - Covers zip files.

THIS THING IS ***KILLING*** ME.
I need to read this tomorrow when i'm not so tired.
https://pymotw.com/2/zipfile/
"""


import zipfile
from .file import *


class Zip(ImmutablePath):
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
		ImmutablePath.__init__(self, k.get('zip', path), **k)
		
		# store password
		self.__pass = pwd
		self.__comp = comp if comp else zipfile.ZIP_DEFLATED
		self.__b64 = b64
		
		# force creation of the file
		with self.open() as z:
			z.close()
	
	@property
	def names(self):
		"""Returns self.namelist()"""
		return self.namelist()
	
	
	# check how tarfile does this
	#@property
	#def members(self):
	#	return self.infolist()
	
	
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
		with self.open() as z:
			try:
				return z.read(member, **k)
			finally:
				z.close()
	
	
	# WRITE
	def write(self, member, data, mode='a', **k):
		"""
		Write data to member (zip path) within the zip file. Default mode
		is 'a'. (To overwrite all contents, use mode='w'.)
		"""
		with self.open(mode) as z:
			try:
				z.writestr(member, data, **k)
			finally:
				z.close()
	
	
	# READER
	def reader(*a,**k):
		raise NotImplementedError('maybe-someday')
	
	
	# WRITER
	def writer(*a,**k):
		raise NotImplementedError('maybe-someday')
		

