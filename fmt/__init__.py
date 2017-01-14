"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under the terms
of the GNU Affero General Public License.

FMT - Text formatting objects with conversion settings.

Use format-based objects as functions that are ready to provide the
customized formatting you need repeatedly. Call the output() method 
to print given text (after formatting) to the terminal. Use the 
format() method if you need the formatted text returned as a string.
"""

from .. import *
import json


JSON_INDENT = DEF_INDENT
JSON_ENCODE = DEF_ENCODE
FORMAT_SEP = '  '



class FormatBase(object):
	"""
	Abstract base formatting class. A FormatBase object is useless as
	a formatter because it has no format() method, but facilitates the
	storage of arguments and keyword args for use when subclasses are
	called to format text.
	
	Use FormatBase-based objects as functions that are ready to provide
	the customized formatting you need repeatedly. Call the output()
	method to print given text (after formatting) to the terminal. Use
	the format() method if you need the formatted text returned as a
	string.
	"""
	
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





#
# NO FORMAT - format/print as-is
#
class NoFormat(FormatBase):
	"""
	Formatter that does not format; Prints or returns "as-is" string.
	"""
	
	def __call__(self, a, **k):
		"""Formats and returns data."""
		return str(a) if a else ''
	
	def output(self, *a, **k):
		"""Format and print data."""
		print (a)





#
# PYTHON FORMAT
#
class Format(FormatBase):
	"""
	Format with the built-in string.format() method.
	"""
	
	def __init__(self, formatString):
		"""
		Pass a format string for the built-in string.format() method. 
		When passed text, this object's format() method will convert it
		to
		"""
		FormatBase.__init__(self, formatString)
	
	def format(self, *a, **k):
		return self.args[0].format(*a, **k)





#
# JSON FORMAT
#
class JSON(FormatBase):
	def format(self, data):
		"""Format data as json strings in a pretty format."""
		return json.dumps(data, **self.kwargs)





#
# JSON DISPLAY - Big, pretty, and readable.
#
class JDisplay(JSON):
	"""JSON in a more human-readable, display format."""
	
	def __init__(self, **k):
		"""Kwargs are passed directly to json.dump(s) functions."""
		k.setdefault('cls', JSONDisplay)
		k.setdefault('indent', JSON_INDENT)
		FormatBase.__init__(self, **k)
	
	def format(self, data):
		"""
		Format data as json strings in a pretty format.
		"""
		return json.dumps(data, **self.kwargs)





#
# JSON FORMAT - Tight as possible; for transmission/storage.
#
class JCompact(JSON):
	"""Compact JSON format."""
	
	def __init__(self, **k):
		"""Kwargs are passed directly to json.dump(s) functions."""
		k.setdefault('separators', (',',':'))
		JSON.__init__(self, **k)

	def format(self, data):
		"""Format as compact json; no unnecessary white space."""
		return ''.join(json.dumps(data, **self.kwargs).splitlines())







#
# JSON JSONEncoder
#  - The pyro module makes extensive use of json data formatting.
#    This encoder is a catch-all for display purposes.
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

