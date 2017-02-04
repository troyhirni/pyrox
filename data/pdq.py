"""
Copyright 2015-2017 Troy Hirni
This file is distributed under the terms of the GNU 
Affero General Public License.

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

Keyword args 'file' and 'member' let you specify a file or zip/tar
member to import as string data. Use Query.splitlines() to split the 
data into a list of lines. Use Query.update() to split individual 
lines into lists. For example:

# EXAMPLE:
import pdq
q = pdq.Query(file="test.txt", encoding='ascii')
q.splitlines()
q.update(lambda o: o.v.split(','))

# EXAMPLE 2 - a quick way to get a grid full of floats
import random
r=[[random.random()*10000 for x in range(0,3)] for y in range(0,20)]
q = pdq.Query(r)
"""

from . import *


class Query(Data):
	def __init__(self, data=None, **k):
		"""
		Argument 'data' can be text, bytes, or a python list. If data
		specification results in byte-text and you know the encoding, 
		pass it as a kwarg: encoding=<enc>. DO NOT pass an encoding with
		anything other than byte strings or file specifications that will
		produce encoded byte strings.
		
		Additional kwargs:
		 - file  : load text from a file; supports text, zip, bzip2, 
		           gzip, and tar files
		 - member: zip and tar files require a name kwarg to identify the
		           item to read from within the file
		 - row   : a custom row type may be specified to replace QRow
		"""
		# encoding; used only if data is text
		self.__encoding = Base.kpop(k, 'encoding')
		
		# type specification for row object
		self.__TRow = k.get('row', QueryRow)
		
		# make sure there's something for data
		self.__data = data = data if data else ''
		
		# allow reading of text or gzip files
		if 'file' in k:
			filepath = Base.kpop(k, 'file')
			reader = Base.ncreate('fs.Path', filepath).reader(**k)
			self.__data = reader.read()
		else:
			# set data and encoding
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
	
	@property
	def encoding(self):
		return self.__encoding
	
	
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
		return self.__TRow.paramgen(self, self.data, *a, **k)
	
	
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








class ParamBase(object):
	"""
	Any class based on Data may make use of generator functions to 
	generate arguments for DataParam objects. DataParam generation will
	be different for different kinds of data. Lists of lists will need
	a value (the list itself) and an index into the list's data (if the
	list consists of sequence objects.
	
	NOTE: The generator methods generate objects of their own class;
	      whatever the subclass is, the generator will return an object
	      of that subclass.
	"""
	
	@classmethod
	def paramgen(cls, caller, value, *a, **k):
		"""
		Return a generator suitable for the given value, which must be 
		of the following types:
		 * sequence - list, set, tupel
		 * mapping  - dict or dict-like with key:value mapping
		"""
		if isinstance(value, (list, set, tuple)):
			return cls.pgseq(caller, value, *a, **k)
		elif isinstance(value, dict):
			return cls.pgdict(caller, value, *a, **k)
		
	@classmethod
	def pgseq(cls, caller, value, *a, **k):
		where = k.get('where')
		for i,v in enumerate(value):
			x = cls(caller, v, i, *a, **k)
			if (not where) or where(x):
				yield x
			
	@classmethod
	def pgdict(cls, caller, value, *a, **k):
		where = k.get('where')
		for key in value.keys():
			x = cls(caller, value[key], key, *a, **k)
			if (not where) or where(x):
				yield x






class ParamData(ParamBase):
	"""
	The Base for classes that make use of callback functions for data
	manipulation. Designed especially for use with lambda functions,
	the properties and method names are abbreviated sharply.
	
	Arguments are typically generated by the caller object and passed
	to this constructor, then the resulting object is sent to a lambda,
	function, or method callback. 
	"""

	def __init__(self, caller, value, key, *a, **k):
		"""
		All arguments are required, though the `key` value may be None if
		the value itself is not a sequence type.
		 * caller = the calling object, which needs to generate params
		            to pass to a callback method;
		 * value  = the value for this particular call to a callback
		            method.
		 * key    = value is typically a sequence type that contains
		            keyed sub-values.
		 
		 Any additional args and kwargs are stored in self.a and self.k
		 respectively.
		"""
		self.c = caller
		self.v = value    # the param value
		self.i = key      # sequence offset or dict key
		self.a = a        # any *args passed to the lambda
		self.k = k        # any **kwargs passed to the lambda
	
	def __getitem__(self, key):
		return self.c[self.i][key]
	
	def __str__(self):
		return str(self.v)
	
	def __call__(self):
		return Chain(self.v)
	
	@property
	def type(self):
		"""Return the type of the current value."""
		return type(self.v)
	
	@property
	def len(self):
		"""Return the length of the current value."""
		return len(self.v)
	
	
	## for sequence type values
	
	# II - subset of current values
	def ii(self, *a):
		"""
		Return given columns as a list. Args types should match the type
		of key required by the current value's data. (See self.type). For
		example, if self.v is a list, args should be integers, but if 
		it's a dict, arg types may vary depending on the type of the dict
		keys you need.
		"""
		return [self.v[i] for i in a]
	
	def di (self, *a):
		"""
		Return a new dict with keys (specified as args) taken from this
		object's value, self.v (which must be a dict or dict-like object.
		"""
		r = {}
		for k in a:
			r[k]=self.v[k]
		return r
	
	# SPLIT
	def split(self, *a):
		"""
		Split the current value, self.v. Args are different from python's
		str.split() method - here's how it works:
		 * If one integer arg is given, it's passed to ''.split() as the 
		   2nd argument, `maxsplit`. In this case, None is the first arg
		   to str.split(), `sep`. LIKE THIS: self.v.split(None, maxsplit)
		 * If two args are given, they're given as arguments directly to
		   str.split. That is: self.v.split(**a), so the args are taken
		   as (sep, max).
		
		This is useful when self.v (the current item value) is a string
		that needs to be converted into a list of values.
		"""
		aa = [None, a[0]] if isinstance(a[0], int) else a
		return self.v[:].split(*aa)
	
	# JOIN
	def join(self, char='', v=None):
		"""
		Return list items joined by given `char`. If v is not specified,
		then self.v is the default.
		"""
		return char.join(v if v else self.v)
	
	# EXTEND
	def extend(self, x, v=None):
		"""
		If two args are given, the second (list) extends the first.
		If one arg is given, it must be a list to extend self.v (only 
		appropriate if self.v is a list). Return the result.
		"""
		v = v if v else self.v[:]
		v.extend(x)
		return v
	
	# APPEND
	def append(self, x, v=None):
		"""
		Append value `x` to list `v`, or to self.v if `v` is None.
		"""
		v = v if v else self.v[:]
		v.append(x)
		return v
	
	# INSERT
	def insert(self, i, x, v=None):
		"""
		Insert `x` at position `i` in list `v`, or in list self.v if `v`
		is None.
		"""
		v = v if v else self.v[:]
		v.insert(i, x)
		return v
	
	# CP - Copy current value
	def cp(self):
		"""Returns a shallow copy of the current value."""
		try:
			return self.v[:]
		except:
			return self.v
	
	
	## utility
	
	def out(self, v=None, fmt=None, *a, **k):
		"""
		If `fmt` is None, value `v` will be printed by print().
		If `fmt` is a valid full import path (string) to a Format class,
		then `v` will be .output() by the resulting Format object.
		"""
		if fmt:
			Base.create(fmt,*a,**k).output(v)
		else:
			print (v if v else self.v)





class Chain(ParamBase):
	"""
	Chain lets you manipulate string, list, and dict data in a single
	line of dot-joined commands. Every method alters self.v, then
	returns self so that another command may follow.
	
	When finished manipulating the data, append .v to the chain of 
	commands. Chain.v is always up-to-date after each command; it makes
	no difference how many commands you chain - when you append .v, the
	value is there.
	
	NOTE: This feature is intended for use inside lambda callbacks, to
	      facilitate setting and manipulation of data where equal signs
	      seem to be forbidden.
	"""
	
	# start with a value...
	def __init__(self, v):
		"""Set the initial value as `v`."""
		self.v = v
	
	
	
	# GENERAL
	def fn(self, fn, *a, **k):
		"""
		Execute the given function passing any args/kwargs, then sets
		this objects value (self.v) to the function result.
		"""
		self.v = fn(self, *a, **k)
		return self
	
	def proc(self, fn, *a, **k):
		"""
		Execute the given function passing any args/kwargs. Function
		return value is ignored.
		"""
		fn(self)
		return self
	
	def noop(self, *a):
		"""
		Ignore any arguments. Return self. This is a good lambda totally
		unrelated things.
		"""
		return self
	
	
	
	# DICT-ONLY
	
	# set a default key value...
	def sdef(self, k, default):
		"""Set a default dict value for the given key."""
		self.setdefault(k, default)
		return self
	
	
	
	# LIST/DICT/ETC...
	
	# set one key's value...
	def kv(self, k, v):
		"""Set self.v[k] = v"""
		self.v[k] = v
		return self
	
	# copy values from like objects (given keys)...
	def cp(self, vv, *a):
		"""
		Pass sequence or map `vv` and a variable number of key or index
		arguments; each *arg key/index value is coppied to self.v at the
		same key or position.
		"""
		for i in a:
			self.v[i] = vv[i]
		return self
	
	# remove values (with given index/keys)
	def rm(self, *a):
		"""Remove all sequence or key values given by *args"""
		try:
			if isinstance(self.v, dict):
				for i in a:
					del(self.v[i])
			else: 
				#sequence
				rr = []
				for i,v in enumerate(self.v):
					if not (i in a):
						rr.append(self.v[i])
				self.v = rr
		except KeyError as ex:
			raise type(ex)('error', xdata(i=i,a=a,python=str(ex)))
		except IndexError as ex:
			raise type(ex)('error', xdata(i=i,a=a,python=str(ex)))
		return self
	
	
	# for each item in self.v
	def each(self, fn, *a, **k):
		for i in self.v:
			fn(self(self.v[i]))
		return self
	
	
	# LIST ONLY
	
	# append new value(s)...
	def add(self, *a):
		self.v.extend(a)
		return self
	
	# insert items...
	def ins(self, i, *a):
		for v in a:
			self.v.insert(i, v)
			i += 1
		return self
	
	# join a list to a string...
	def join(self, c):
		self.v = c.join(self.v)
		return self
	
	
	
	# STRING ONLY
	
	# split text...
	def sp(self, *a, **k):
		self.v = self.v.split(*a, **k)
		return self
	
	
	
	# MANIPULATING EXTERNAL OBJECTS
	
	# set an external object's item value.
	def setkv(self, obj, key, value):
		"""
		Set the value associated with the given object's key. This is
		meant to facilitate population of lists, dicts, etc... that are
		in the global scope.
		
		d = {}
		x.each(lambda p: p.setkv(d, p.v[0], p.v[1]))
		print (d)
		"""
		obj[key] = value
		return self





			



class QueryRow(ParamData):
	"""
	The parameter object passed to callback functions/lambdas.
	"""
	def __init__(self, query, value, item, *a, **k):
		ParamData.__init__(self, query, value, item, *a, **k)
		self.q = query # same as self.c
	
	def qq(self, v=None, **k):
		"""
		Returns a new Query object giving arg `v` or self.v if `v` is 
		None. Keyword arguments also work, so a file kwarg can load a 
		file (ignoring v and self.v altogether).
		"""
		return Query(v=v if v else self.v, **k)
