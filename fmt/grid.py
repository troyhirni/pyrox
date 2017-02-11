"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under the terms
of the GNU Affero General Public License.

GRID - Display a list of lists (of equal length) in a grid.

The grid module defines a Grid class that formats a list containing
[a set of lists of equal length] into a grid for display. It also 
defines the List class, a special-case single-column Grid.

"""


from . import *



class Grid (FormatBase):
	"""
	Format list of lists into a grid.
	
	>>> grid.Grid().output(list([1,2],[3,4]))
	"""
	
	def __init__(self, **k):
		"""
		Kwarg `sep` defaults to a single space; Optional `cellformat` 
		kwarg specifies a callable to apply to each cell (default: str).
		"""
		self.__ind = k.get('indent', "")
		self.__sep = k.get('sep', FORMAT_SEP)
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
		ind = k.get("indent", self.__ind)
		fmt = k.get("cellformat", self.__fmt)
		if fmt:
			grid = self.formatgrid(grid, fmt)
		
		r = []
		f = self.formatstring(grid)
		for row in grid:
			r.append("%s%s" % (ind, f.format(*row)))
		return '\n'.join(r)






class List(Grid):
	"""
	Simple list formatter - displays a list's items in individually
	numbered rows.
	"""
	def format(self, dataList, **k):
		start = k.get('start', 1)
		i = start
		flist = []
		title = k.get('title')
		if title:
			for x in dataList:
				flist.append([title(i), x])
				i += 1
		else:
			for x in dataList:
				flist.append([i, x])
				i += 1
		
		return Grid.format(self, flist, **k)

