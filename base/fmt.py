"""
Copyright 2014-2015 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

JSON format objects with specialized conversion settings.
"""

try:
	from ..base import *
except:
	from base import *


JSON_ENCODE = DEF_ENCODE
JSON_INDENT = DEF_INDENT



class Formatting(object):
	"""Base formatting class. Does nothing to format."""
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
	
	def __call__(self, data):
		"""Formats and returns data."""
		return self.format(data)

	def format(self, data):
		"""Place-holder. Returns string value of given data."""
		return str(data)
	
	def output(self, data):
		"""Format and print data."""
		print (self.format(data))


#
# JSON - FOR DISPLAY
#
class JFormat(Formatting):
	"""JSON in display format."""
	
	def __init__(self, **k):
		"""Kwargs are passed directly to json.dump(s) functions."""
		k.setdefault('cls', JSONDisplay)
		k.setdefault('indent', JSON_INDENT)
		#k.setdefault('encoding', JSON_ENCODE) #damn python3
		Formatting.__init__(self, **k)
	
	def format(self, data):
		"""Format data as json strings in a pretty format."""
		return json.dumps(data, **self.kwargs)


#
# JSON - COMPACT
#
class JCompact(JFormat):
	"""Compact JSON format."""
	
	def __init__(self, **k):
		"""Kwargs are passed directly to json.dump(s) functions."""
		k.setdefault('indent', 0)
		k.setdefault('separators', (',',':'))
		JFormat.__init__(self, **k)

	def format(self, data):
		"""Format as compact json; no unnecessary white."""
		return ''.join(json.dumps(data, **self.kwargs).splitlines())


#
# JSON ENCODER
#
class JSONDisplay(json.JSONEncoder):
	"""
	Handles unparsable types by returning their representation to be
	stored as a string.
	"""
	def default(self, obj):
		try:
			return json.JSONEncoder.default(self, obj)
		except TypeError:
			return repr(obj)


