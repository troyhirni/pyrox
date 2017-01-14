"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under the terms
of the GNU Affero General Public License.

TABLE - Display a list's items in a tabulated grid.
"""

from .grid import *


class Table(Grid):
	"""
	Formats a list into a grid of specified width (by converting the list
	into a "list of lists" suitable for processing by Grid).
	"""
	def __init__(self, **k):
		"""
		Keyword argument `width` replaces the default number of columns  
		into which any `data` list given to the format() method will be 
		split. Default is 1. Any additional kwargs will be passed on to  
		Grid's constructor.
		"""
		Grid.__init__(self, **k)
		self.__width = k.get('width', 1)
		if self.__width < 1:
			raise Exception ('invalid-width')
	
	# FORMAT
	def format(self, data, **k):
		"""
		Format the given list `data` by separating it into a grid (a list of
		lists) and passing it to Grid.format. Keyword arguments are passed
		on to Grid.format().
		"""
		datalist = self.merge(data, **k)
		return Grid.format(self, datalist, **k)
	
	# MERGE
	def merge(self, data, **k):
		width = k.get('width', self.__width)
		y = []
		x = 0
		line = []
		for d in data:
			if x <= self.__width:
				line.append(d)
				x += 1
			if x == self.__width:
				y.append(line)
				line = []
				x = 0
		
		if line:
			line.extend(''.split(',')*width)
			y.append(line[0:width])
		
		return y
