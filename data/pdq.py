"""
Copyright 2015-2017 Troy Hirni
This file is distributed under the terms of the GNU 
Affero General Public License.

PDQ - Python Data Query

The rows, select, update, delete and each methods accept keyword
'where' - a callable that returns True for matching records.
"""

from .. import *


class Query(object):
	def __init__(self, data=[], **k):
		"""
		Argument 'data' can be text, bytes, or a python list. If you 
		know the encoding of your text, pass it as encoding=<enc>.
		"""
		self.Row =  k.get('Row', QRow)
		if 'encoding' in k:
			self.encoding = k['encoding']
			self.__data = data.decode(self.encoding)
		else:
			self.__data = data
		self.__undo = self.__data
	
	
	def __getitem__(self, key):
		return self.data[key]
	
	
	@property
	def len(self):
		"""Return self.data length."""
		return len(self.data)
	
	@property
	def type(self):
		return type(self.__data)
	
	@property
	def data(self):
		return self.__data
	
	@data.setter
	def data(self, d):
		if d == self: raise ValueError('pdq-data-invalid')
		self.__undo = self.__data
		self.__data = d
	
	
	# UTILITY METHODS
	
	def head(self, *a):
		"""Return, from the given offset, the given number of lines."""
		x,y = (a[0],sum(a[0:2])) if len(a)>1 else (0, a[0] if a else 9)
		try:
			lines = self.data.splitlines()
			try:
				# hopefully it's unicode
				return '\n'.join(lines[x:y])
			except TypeError:
				# or bytes
				return b'\n'.join(lines[x:y])
		except AttributeError:
			try:
				# or already a list
				return self.data[x:y]
			except:
				# or something python can turn into a string
				return str(self.data).splitlines()[x:y]
		
	def peek(self, *a):
		h = self.head(*a)
		if isinstance(h, (bytes,basestring)):
			print (h)
		else:
			for l in h:
				print (l)
	
	def rows(self, *a, **k):
		"""Returns a generator of self.Rows for matching rows."""
		where = k.get('where')
		for i,v in enumerate(self.data):
			x = self.Row(self, i, v, *a, **k)
			if (not where) or where(x):
				yield x
	
	#
	# QUERY METHODS - Always return a Query object.
	#
	
	def undo(self):
		"""
		Limited undo; works like the old-fashioned undo - undo twice to
		redo.
		"""
		u = self.__data
		self.__data = self.__undo
		self.__undo = u
		return self
	
	def splitlines(self, *a, **k):
		self.data = self.data.splitlines(*a, **k)
		return self
	
	def select(self, fn=None, *a, **k):
		"""Returns a new Query with a copy of matching records."""
		result = []
		for row in self.rows(*a, **k):
			result.append(fn(row) if fn else row.v[:])
		return Query(result)
	
	def sort(self, fn=None, **k):
		"""Sort self.data, by the results of fn if given."""
		fn = k.get('desc', k.get('asc', fn))
		if fn:
			order = []
			for row in self.rows():
				order.append([fn(row), row.v])
			reverse(order).sort() if k.get('desc') else order.sort()
			self.data = map(lambda o: o[1], order)
		else:
			if k.get('desc'):
				self.data = reverse(d)
			else:
				sdata = self.data[:]
				sdata.sort()
				self.data = sdata
		return self
	
	def update(self, fn, *a, **k):
		"""Update matching self.data rows to fn result; Return self."""
		self.__undo = self.select().data
		result = []
		for row in self.rows(*a, **k):
			result.append(fn(row))
		self.data = result
		return self
	
	def delete(self, *a, **k):
		"""
		Delete matching rows from self.data; If no where kwarg, delete all;
		Return self.
		"""
		fn = k.get('where', lambda *a,**k: False)
		k['where'] = lambda *a, **k: not fn(*a, **k) # reverse where...
		
		# ...deletes by selecting and keeping what should NOT be deleted.
		newq = self.select(*a, **k)
		self.data = newq.data
		return self
	
	def each(self, fn, *a, **k):
		"""Execute fn for matching rows."""
		for row in self.rows(*a, **k):
			fn(row)
		return self



class QRow(object):
	"""
	The 'r' value used in the fn, where, and order lambdas, above. 
	Method and variable names are small to accomodate use tight spaces.
	For self-documentation in code, some variable names are available 
	as properties.
	"""
	def __init__(self, query, item, value, *a, **k):
		self.q = query
		self.i = item
		self.v = value
		self.a = a
		self.k = k
	
	def __getitem__(self, key):
		return self.q[self.i][key]
	
	def __str__(self):
		return str(self.q[self.i])
	
	@property
	def item(self):
		"""Enumeration item, starting at zero."""
		return self.i
	
	@property
	def value(self):
		"""
		The enumeration value. Eg, when q.data is type list, this is the
		current list item; when dict, it's the dict key, etc...
		"""
		return self.v
	
	@property
	def type(self):
		"""Return the type of the current value."""
		return type(self.v)
	
	def ii(self, *a):
		"""Return given columns as a list."""
		return [self.v[c] for c in a]
	
	def split(self, *a):
		"""
		Split the enumeration value. Args are different from python's
		''.split - if first arg is int, it's used as the 2nd argument
		and None is the first split argument. If there are two args, 
		they're passed as (sep, max) to python's split method.
		"""
		aa = [None, a[0]] if isinstance(a[0], int) else a
		return self.v.split(*aa)
	
	def join(self, char):
		"""Return list items joined by given char."""
		return char.join(self.v)
	
	def extend(self, *a):
		"""
		If two args are given, the second (list) extends the first.
		If one arg is given, it must be a list to extend self.v (only 
		appropriate if self.v is a list). Return the result.
		"""
		x.extend(y)
		return x
	
	def cp(self):
		"""Return a copy of this row."""
		try:
			return self.v[:]
		except:
			return self.v

