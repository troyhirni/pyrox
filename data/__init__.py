"""
Copyright 2015-2017 Troy Hirni
This file is distributed under the terms of the GNU 
Affero General Public License.

DATA - Data Utility

The data package supports the extraction and manipulation of data 
from a variety of databases and formatted text files, generation of
random values, and text-scanning based on unicode-related meta-data 
as well as characters.
"""

from .. import *



class Data(Base):
	pass



#
# UNDER CONSTRUCTION - EXPERIMENTAL
#
class FFactory(object):
	"""
	TO DO: Check this to make sure it's faster than just using Factory.
	       I think it almost has to be, but I can't be sure until it's
	       tested.
	
	THIS WILL ALMOST CERTAINLY MOVE TO SOME OTHER LOCATION...
	
	...OR IT MAY DISAPPEAR ENTIRELY.
	
	For now, I'm just keeping it here so as to have it backed up.
	"""
	def __init__(self, fnspec):
		self.__spec = fnspec
	
	@property
	def fn(self):
		try:
			return self.__fn
		except KeyError:
			self.__fn = TFactory(self.__spec).type
			return self.__fn


class Bytes(object):
	_bzip       = FFactory('bz2.compress')
	_bunzip     = FFactory('bz2.decompress')
	_hexlify    = FFactory('binascii.hexlify')
	_unhexlify  = FFactory('binascii.unhexlify')
	_rlecode    = FFactory('binascii.rlecode_hqx')
	_rledecode  = FFactory('binascii.rledecode_hqx')
	_gzip       = FFactory("zlib.compress")
	_gunzip     = FFactory("zlib.decompress")
	_b64encode  = FFactory('base64.b64encode')
	_b64decode  = FFactory('base64.b64decode')
	_b64encodes = FFactory('base64.standard_b64encode')
	_b64decodes = FFactory('base64.standard_b64decode')
	_b64encodeu = FFactory('base64.urlsafe_b64decode')
	_b64decodeu = FFactory('base64.urlsafe_b64decode')
	_b32encode  = FFactory('base64.b32encode')
	_b32decode  = FFactory('base64.b32decode')
	_b16encode  = FFactory('base64.b16encode')
	_b16decode  = FFactory('base64.b16decode')
	
	def __init__(self, bbytes=None):
		self.__bytes = bbytes or b''
	
	@property
	def bytes(self):
		return self.__bytes
	
	@bytes.setter
	def bytes(self, bb):
		self.__bytes = bb
	


"""
class ByteFn(object):
	
	Byte manipulation cover functions - EXPERIMENTAL
	
	Several python modules that manipulate bytes are covered in this
	class. No python library modules are loaded until a method defined
	there is actually called, keeping the memory footprint as low as is
	possible.
	
	This class is experimental. If kept, it may be moved to a different
	module.
	
	_bzip       = Factory('bz2.compress')
	_bunzip     = Factory('bz2.decompress')
	_hexlify    = Factory('binascii.hexlify')
	_unhexlify  = Factory('binascii.unhexlify')
	_rlecode    = Factory('binascii.rlecode_hqx')
	_rledecode  = Factory('binascii.rledecode_hqx')
	_gzip       = Factory("zlib.compress")
	_gunzip     = Factory("zlib.decompress")
	_b64encode  = Factory('base64.b64encode')
	_b64decode  = Factory('base64.b64decode')
	_b64encodes = Factory('base64.standard_b64encode')
	_b64decodes = Factory('base64.standard_b64decode')
	_b64encodeu = Factory('base64.urlsafe_b64decode')
	_b64decodeu = Factory('base64.urlsafe_b64decode')
	_b32encode  = Factory('base64.b32encode')
	_b32decode  = Factory('base64.b32decode')
	_b16encode  = Factory('base64.b16encode')
	_b16decode  = Factory('base64.b16decode')
"""
