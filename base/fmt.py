"""
Copyright 2014-2016 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

JSON format objects with specialized conversion settings.
"""

try:
	from ..base import *
except:
	from base import *

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



#
# JSON FORMAT
#
class JSON(FormatBase):
	def format(self, data):
		"""Format data as json strings in a pretty format."""
		return json.dumps(data, **self.kwargs)

	
class JFormat(JSON):
	"""JSON in display format."""
	
	def __init__(self, **k):
		"""Kwargs are passed directly to json.dump(s) functions."""
		k.setdefault('cls', JSONDisplay)
		k.setdefault('indent', JSON_INDENT)
		FormatBase.__init__(self, **k)
	
	def format(self, data):
		"""Format data as json strings in a pretty format."""
		return json.dumps(data, **self.kwargs)


class JCompact(JSON):
	"""Compact JSON format."""
	
	def __init__(self, **k):
		"""Kwargs are passed directly to json.dump(s) functions."""
		k.setdefault('separators', (',',':'))
		JSON.__init__(self, **k)

	def format(self, data):
		#Format as compact json; no unnecessary white.
		return ''.join(json.dumps(data, **self.kwargs).splitlines())


"""
# JSON - Utility
class JSONDisplay(json.JSONEncoder):
	def default(self, obj):
		try:
			return json.JSONEncoder.default(self, obj)
		except TypeError:
			return repr(obj)
"""


#
# SPECIALTY
#
class Grid (FormatBase):
	"""Format list of lists into a grid."""
	
	def __init__(self, sep=' ', **k):
		"""
		Arg sep defaults to a single space; Optional 'cellformat' kwarg
		specifies a callable to apply to each cell (default: str).
		"""
		self.__sep = sep
		self.__fmt = k.get('cellformat') or str
		FormatBase.__init__(self)
	
	
	def formatstring(self, grid):
		"""Generate a format string for the given grid."""
		glen = len(grid[0])
		cmax = [0 for x in range(glen)]
		for row in grid:
			for c,col in enumerate(row):
				L = len(col)
				if L > cmax[c]:
					cmax[c] = L
		
		fstr = map(lambda x: "{:<%s}" % x, [cmax[x] for x in range(0, glen)])
		return self.__sep.join(fstr)
	
	
	def formatgrid(self, grid, fmt):
		"""Duplicate grid, but with each item formatted by fmt."""
		
		# duplicate grid with formatted items
		fgrid = []
		for gRow in grid:
			cols = []
			for col in gRow:
				# copy each cell from grid to fgrid, but formatted
				cols.append(fmt(col))
			fgrid.append(cols)
		
		# return the copy
		return fgrid
	
	
	def format(self, grid, **k):	
		
		# format grid
		fmt = k.get("cellformat", self.__fmt)
		if fmt:
			grid = self.formatgrid(grid, fmt)
		
		r = []
		f = self.formatstring(grid)
		for row in grid:
			r.append(f.format(*row))
		return '\n'.join(r)
