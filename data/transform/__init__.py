"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

TRANSFORM - Transform objects to text/text to objects

This module is intended to transform formatted text to objects. 
Currently only JSON is supported. The idea is to provide a way to
slip data transformation into file read/write methods.

        EXPERIMENTAL!  This module is experimental.
	
This module may not be here for long; if it remains, it will almost
certainly experience lots of changes.
"""


from .. import *
import json




class TransformText(object):
	
	def totext(self, *a, **k):
		raise NotImplementedError()
	
	def fromtext(self, *a, **k):
		raise NotImplementedError()




class TransformJson(TransformText):
	
	def __init__(self, display=False, **k):
		self.__fmt = Base.ncreate(
			'fmt.JDisplay' if display else 'fmt.JCompact'
		)
		
		# save a microsecond or two...
		totext = self.__fmt
	
	
	def totext(self, obj):
		"""Convert the given object to JSON text."""
		return self.__fmt(obj)	
	
	
	def fromtext(self, text, **k):
		"""
		Convert the given text to json, applying any kwargs to the
		json.loads() function.
		"""
		return json.loads(text, **k)






