"""
Copyright 2014-2015 Troy Hirni
This file is distributed under the terms of the GNU 
Affero General Public License.

PDQ - Python Data Query

The rows, select, update, delete and each methods accept keyword
'where' - a callable that returns True for matching records.
"""

from . import fs

try:
	from ..base import *
except:
	from base import *


class Query(object):
	def __init__(self, data=[], **k):
		"""Pass list data or kwarg file=<filepath> to load a text file."""
		self.Row =  k.get('Row', QRow)
		if 'file' in k:
			self.data = fs.File(k['file']).read()
		else:
			self.data = data
	
	def __getitem__(self, key):
		return self.data[key]
	
	@property
	def len(self):
		"""Return self.data length."""
		return len(self.data)
		
	def head(self, x=0, y=11):
		"""Return string with lines[:x] or lines[x:x+y]"""
		x,y = (x,x+y) if y else (0,x)
		if isinstance(self.data, basestring):
			return '\n'.join(self.data.splitlines()[x:y])
		return self.data[x:y]
	
	def peek(self, *a):
		h = self.head(*a)
		if isinstance(h, basestring):
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
	
	def select(self, fn=None, *a, **k):
		"""Returns a new Query with a copy of matching records."""
		result = []
		for row in self.rows(*a, **k):
			result.append(fn(row) if fn else row[:])
		return Query(result)
	
	def sort(self, fn=None):
		"""Sort self.data, by the results of fn if given."""
		order = []
		for row in self.rows():
			order.append([fn(row), row.v])
		order.sort()
		self.data = map(lambda o: o[1], order)
		return self
	
	def update(self, fn, *a, **k):
		"""Update matching self.data rows to fn result; Return self."""
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
	The 'r' value used in the fn, where, and order lambdas, above. Method
	and variable names are small to accomodate use tight spaces :)
	"""
	def __init__(self, query, key, value, *a, **k):
		self.q = query
		self.i = key
		self.v = value
		self.a = a
		self.k = k
	
	def __getitem__(self, key):
		return self.q[self.i][key]
	
	def __str__(self):
		return str(self.q[self.i])
	
	def ii(self, *keys):
		"""Keys to select. eg, q.select(lambda r: r.ii(0,2))"""
		return [self[k] for k in keys]
