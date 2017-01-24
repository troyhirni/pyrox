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


class Data(object):
	"""
	EXPERIMENTAL - This class may disappear in future versions.
	I'm playing with this idea; at very least I'll use it to help me
	test the Cursor class.
	"""
	@classmethod
	def cursor(cls, *a, **k):
		return Base.ncreate('data.cursor.Cursor', *a, **k)
	
	@classmethod
	def parsehtml(cls, *a, **k):
		return Base.ncreate('data.dom.parse', *a, **k)
	



