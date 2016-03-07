"""
Copyright 2014-2016 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

JSON format objects with specialized conversion settings.
"""

try:
	from ..fmt import *
except:
  from fmt import *


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
