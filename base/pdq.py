"""
Copyright 2015-2016 Troy Hirni
This file is distributed under the terms of the GNU 
Affero General Public License.

PDQ - Python Data Query

Helpful utility for mining data imported from text files.

The rows, select, update, delete and each methods accept keyword
'where' - a callable that returns True for matching records.
"""

try:
	from ..base import *
except:
	from base import *


class Query(object):
	def __init__(self, data=[], **k):
		"""
		Argument 'data' can be text, bytes, or a python list. If you 
		know the encoding of your text, pass it as encoding=<enc>.
		Otherwise, bytes are treated as bytes and may not look and
		work quite right - especially in python 3.
		"""
		self.Row =  k.get('Row', QRow)
		if 'encoding' in k:
			self.encoding = k['encoding']
			data = data.decode(self.encoding) 
		
		self.data = data
		
	
	def __getitem__(self, key):
		return self.data[key]
	
	@property
	def len(self):
		"""Return self.data length."""
		return len(self.data)
		
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
	
	def select(self, fn=None, *a, **k):
		"""Returns a new Query with a copy of matching records."""
		result = []
		for row in self.rows(*a, **k):
			result.append(fn(row) if fn else row[:])
		return Query(result)
	
	def sort(self, fn=None):
		"""Sort self.data, by the results of fn if given."""
		if fn:
			order = []
			for row in self.rows():
				order.append([fn(row), row.v])
			order.sort()
			self.data = map(lambda o: o[1], order)
		else:
			self.data.sort()
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

