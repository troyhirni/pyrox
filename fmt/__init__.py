"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under the terms
of the GNU Affero General Public License.

FMT - Text formatting objects with conversion settings.

Format-based objects store formatting parameters and use them to
return or output formatted text for data given to the `format()` or
`output()` methods.

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
	
	def __call__(self, data, **k):
		"""Return `data` cast as a string."""
		return str(a) if a else ''
	
	def output(self, data):
		"""Print `data`."""
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
		FormatBase.__init__(self)
		self.__formatstr = formatString
	
	
	def format(self, *a, **k):
		"""
		Pass args and kwargs - the values to be formatted into the format
		method of the `formatString` given to the constructor.
		
		f = Format('{0}, {1}, {2}')
		print (f.format('a', 'b', 'c'))
		"""
		return self.self.__formatstr.format(*a, **k)





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
			try:
				return json.JSONEncoder.default(self, obj)
			except Exception:
				try:
					return repr(obj)
				except:
					return "<%s>" % obj.__class__.__name__
		except:
			raise

