"""
Copyright 2014-2016 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

JSON format objects with specialized conversion settings.
"""

try:
	from ...plugin import *
except:
	from plugin import *

import json


JSON_ENCODE = DEF_ENCODE
JSON_INDENT = DEF_INDENT


class FormatBase(object):
	"""Abstract base formatting class."""
	
	def __init__(self, *a, **k):
		self.__a = a
		self.__k = k
	
	@property
	def args(self):
		"""Formatting arguments."""
		return self.__a
	
	@property
	def kwargs(self):
		"""Formatting keyword arguments."""
		return self.__k
	
	def __call__(self, *a, **k):
		"""Formats and returns data."""
		return self.format(*a, **k)
	
	def output(self, *a, **k):
		"""Format and print data."""
		print (self.format(*a, **k))



class NoFormat(FormatBase):
	"""Return/Print as-is."""
	
	def __call__(self, *a, **k):
		"""Formats and returns data."""
		return str(a[0]) if a else ''
	
	def output(self, *a, **k):
		"""Format and print data."""
		print (a[0] if a else '')



#
# PYTHON FORMAT
#
class Format(FormatBase):
	"""Format with the built-in string.format() method."""
	
	def __init__(self, formatString):
		"""
		Pass a format string for the built-in string.format() method.
		"""
		FormatBase.__init__(self, formatString)
	
	def format(self, *a, **k):
		return self.args[0].format(*a, **k)



