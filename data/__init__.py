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
		
	@classmethod
	def mreader(cls, **k):
		filepath = Base.kpop(k, 'file')
		member = Base.kpop(k, 'member')
		mm = Base.ncreate('fs.mime.Mime', filepath)
		try:
			return mm.file()
		except Exception as ex:
			raise type(ex)('mime-read-fail', xdata(
					member=member, filepath=filepath, kwargs=k, 
					mime=mm.guess if mm else None
				))
