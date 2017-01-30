"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under the terms
of the GNU Affero General Public License.

MIME - Utility for finding file types and the fs object to open them

Mime is a one-time-use object in which all values are set in the
constructor. Properties make results available.

   UNDER CONSTRUCTION! - This module is under construction!
                         Some portions (lower) are experimental.
"""

from .. import *
import mimetypes

class Mime(object):
	def __init__(self, url, strict=False):
		"""
		Pass a url (a file name will do). Optional `strict` argument
		limits results to IANA specifications, but default is to allow
		well-known file types, as well.
		"""
		self.__url = url # the file name will do
		self.__strict = strict
		
		r = mimetypes.guess_type(url, strict)
		self.__guess = r
		self.__mimet = r[0]
		self.__enc = r[1]
		
		t,st = self.__mimet.split('/') if self.__mimet else (None,None)
		self.__type = t
		self.__subtype = st
	
	def __str__(self):
		return "<Mime %s>" % (str(self.__guess))
	
	@property
	def guess(self):
		return self.__guess
	
	@property
	def strict(self):
		return self.__strict
	
	@property
	def mimetype(self):
		return self.__mimetype
	
	@property
	def enc(self):
		"""
		Returns either 'compress', 'gzip', or None. 
		BE AWARE: This is NOT unicode encoding!
		"""
		return self.__enc
	
	@property
	def type(self):
		return self.__type
	
	@property
	def subtype(self):
		return self.__subtype
	
	
	#
	# EXPERIMENTAL.
	# The following methods seem a bit bulky or possibly ill-placed.
	# It's possible this functionality should be relocated/reorganized.
	#
	def file(self, **k):
		## Return a suitable fs file object.
		
		# set this object as a keyword argument
		k['mime']=self
		
		# application is zip or tar
		if self.__type == 'application':
			if self.__subtype == 'zip':
				return Base.ncreate('fs.zip.Zip', self.__url, **k)
			elif self.__subtype == 'x-tar':
				return Base.ncreate('fs.tar.Tar', self.__url, **k)
			elif self.__subtype == 'json':
				transform = Base.ncreate('data.transform.TransformJson', **k)
				return Base.ncreate(
					'fs.file.TransformFile', transform, self.__url, **k
				)
		
		# gzip encoded
		elif self.__enc == 'gzip':
			return Base.ncreate('fs.gzip.Gzip', self.__url, **k)
		
		# bzip2 encoded
		elif self.__enc == 'bzip2':
			return Base.ncreate('fs.bzip.Bzip', self.__url, **k)
		
		# text/csv (or tsv)
		elif self.__type == 'text':
			if self.__subtype in ['csv', 'tab-separated-values']:
				return Base.ncreate('fs.csv.CSV', self.__url, **k)
		
		# last resort: any kind of file
		return Base.ncreate('fs.file.File', self.__url, **k)
	
	

	# something's not going right here. try again some other way.
	# it works for 
	"""
	#
	# READER (Class-method)
	#  - Select the correct reader for tar and zip file members (or 
	#    for regular files.
	#
	def reader(self, **k):
		## Return a suitable stream reader.
		
		# a member is specified
		if 'member' in k:
			member = k['member']
			
			# get the member's mime info
			mm = type(self)(member)
			
			# if it's text/csv, create and return a CSVReader using the
			# tar or zip file's reader
			if mm.type == 'text':
				if mm.subtype in ['csv', 'tab-separated-values']:
					return Base.ncreate(
						'fs.csv.CSVReader', self.file().reader(member)
					)
			
			# if it's application/json, return a data reader
			elif mm.type == 'application':
				if mm.subtype == 'json':
					return Base.ncreate(
						'fs.tfile.DataReader', self.file().reader(member)
					)
		
		# if none of the above (or if there's no member kwarg), then just
		# return a normal reader
		return self.file().reader()
		
	"""


