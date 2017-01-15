"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under the terms
of the GNU Affero General Public License.

MIME - Utility for finding file types and the fs object to open them

Mime is a one-time-use object in which all values are set in the
constructor. Properties make results available.

   UNDER CONSTRUCTION! - This module is under construction!
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
	
	def file(self):
		
		# application is zip or tar
		if self.__type == 'application':
			if self.__subtype == 'zip':
				return Base.ncreate('fs.zip.Zip', self.__url)
			elif self.__subtype == 'x-tar':
				return Base.ncreate('fs.tar.Tar', self.__url)
		
		# gzip encoded
		elif self.__enc == 'gzip':
			return Base.ncreate('fs.gzip.Gzip', self.__url)
		
		# gzip encoded
		elif self.__enc == 'bzip2':
			return Base.ncreate('fs.bzip.Bzip', self.__url)
		
		# any kind of text file
		if self.__type == 'text':
			return Base.ncreate('fs.file.File', self.__url)
		
		raise Exception('file-opener-not-available')

