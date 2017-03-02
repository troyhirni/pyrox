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




class ByteFn(object):
	"""
	Byte manipulation cover functions - EXPERIMENTAL
	
	Several python modules that manipulate bytes are covered in this
	class. No python library modules are loaded until a method defined
	there is actually called, keeping the memory footprint as low as is
	possible.
	
	This class is experimental. If kept, it may be moved to a different
	module.
	"""
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
	
