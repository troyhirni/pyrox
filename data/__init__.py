"""
Copyright 2015-2017 Troy Hirni
This file is distributed under the terms of the GNU 
Affero General Public License.

DATA - Data Utility


  - thinking aobut this... not sure yet...


"""

from .. import *


class DataUtil(Base):

	# this might move to fs or to Base
	@classmethod
	def mfile(cls, *a, **k):
		return Base.ncreate('fs.mime.Mime', *a **k).file()
	
	@classmethod
	def cursor(cls, *a, **k):
		return Base.ncreate('data.cursor.Cursor', *a **k)
		
