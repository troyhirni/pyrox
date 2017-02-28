"""
Copyright 2015-2017 Troy Hirni
This file is part of the pyro project, distributed under the terms
of the GNU Affero General Public License.

PDQ - Python Data Query

PDQ is a tool for quick exploration and manipulation of python lists.
Create a Query object passing a list or text to the constructor. Use 
Query methods to massage the data until it's just what you need. The 
rows, select, update, delete and each methods accept keyword `where` 
- a callable that returns True for matching records.

The head(), peek(), and grid() methods display small sections of 
current data in various formats, and fmt() is available to help you
format (or output) the data in various other ways. The data property
returns the data itself, or lets you completely reset the data. There
is even a one-time undo() method in case you get unexpected results.
Calling undo() repeatedly toggles self.data between the previous and
current values.

Use keyword arg `file` to specify a text file to import as string 
data.

# EXAMPLE:
import pdq
q = pdq.Query(file="space-separated-values.txt", encoding='ascii')
q.splitlines()
q.update(lambda o: o.v.split())

The `file` path's mime type determines the type of reader to be
returned, so `file` may specify gzip, bzip, etc..

If reading from a zip or tar file, use the `member` keyword to 
specify the file within the archive.

When specfiying a csv file, rows are read from the file as lists of
string values.

# EXAMPLE:
import pdq
q = pdq.Query(file="myarchive.zip", member="some.csv")
q.peek()
"""

from .param import *


class Query(Base):
	def __init__(self, data=None, **k):
		"""
		Argument 'data' can be text, bytes, or a python list. If data
		specification results in byte-text and you know the encoding, 
		pass it as a kwarg: encoding=<enc>. DO NOT pass an encoding with
		anything other than byte strings or file specifications that will
		produce encoded byte strings.
		
		Additional kwargs:
		 - row    : a custom row type may be specified to replace QRow
		 
		Additional kwarg sets:
		 * stream
		   - stream  : any object with a read() method that will read its
		               contents into the Query object's data.
		 * file (and member, if applicable)
		   - file    : load text from a file; supports all file wrappers.
		   - member  : zip and tar files require a `member` kwarg to 
		               identify the item within the file to read
		"""
		# encoding; used only if data is text
		self.__encoding = k.get('encoding', None)
		
		# type specification for row object
		self.__TRow = k.get('row', QRow)
		
		# make sure there's something for data
		self.__data = data = data if data else ''
		
		# allow reading of text or gzip files
		if 'file' in k:
			reader = Base.path(k.pop('file')).reader(**k)
			self.__data = reader.read()
		elif 'stream' in k:
			self.__data = k['stream'].read()
		else:
			self.__data = data
		
		# if 'encoding' is specified, decode bytes only
		if self.__encoding and isinstance(self.__data, pxbytes):
			self.__data = self.__data.decode(self.__encoding)
		
		# prep undo
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
				# unicode
				self.lasthead = 'unicode'
				return '\n'.join(lines[x:y])
			except TypeError:
				# bytes
				self.lasthead = 'bytes'
				return b'\n'.join(lines[x:y])
		except AttributeError:
			try:
				# list
				self.lasthead = 'list'
				return self.data[x:y]
			except:
				# other - something python can turn into a string
				self.lasthead = 'other'
				fmt = Base.ncreate('fmt.JDisplay')
				return fmt(self.data).splitlines()[x:y]
				#return str(self.data).splitlines()[x:y]
		
	def peek(self, *a):
		"""Print each line. Same args as head()."""
		h = self.head(*a)
		if isinstance(h, (bytes,basestring)):
			print (h)
		else:
			for l in h:
				print (l)
	
	def grid(self, *a, **k):
		"""
		Output a grid. Same args as head(); Kwargs passed to grid.Grid
		constructor.
		"""
		Base.ncreate('fmt.grid.Grid', **k).output(self.head(*a))
	
	def rows(self, *a, **k):
		"""
		Returns a generator of type QRow for matching rows.
		"""
		return self.__TRow.paramgen(self.data, self, *a, **k)
	
	
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
			try:
				result.append(fn(row) if fn else row.v[:])
			except Exception as ex:
				raise type(ex)('callback-fail', xdata(i=row.i, v=row.v,
					python=str(ex))
				)	
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

			



class QRow(Param):
	"""
	The parameter object passed to callback functions/lambdas.
	"""
	
	@classmethod
	def paramgen(cls, data, caller, *a, **k):
		if isinstance(data, (list, set, tuple)):
			return cls.pgseq(data, caller, *a, **k)
		elif isinstance(data, dict):
			return cls.pgdict(data, caller, *a, **k)
		
	@classmethod
	def pgseq(cls, data, caller, *a, **k):
		where = k.get('where')
		for i,v in enumerate(data):
			x = cls(caller, v, i, *a, **k)
			if (not where) or where(x):
				yield x
			
	@classmethod
	def pgdict(cls, data, caller, *a, **k):
		where = k.get('where')
		for key in data.keys():
			x = cls(caller, data[key], key, *a, **k)
			if (not where) or where(x):
				yield x

	def __init__(self, query, value, item, *a, **k):
		Param.__init__(self, value, item)# no args/kwargs! #, *a, **k)
		self.q = query
	
	def qq(self, v=None, **k):
		"""
		Returns a new Query object giving arg `v` or self.v if `v` is 
		None. Keyword arguments also work, so a file kwarg can load a 
		file (ignoring v and self.v altogether).
		"""
		return Query(v=v if v else self.v, **k)
