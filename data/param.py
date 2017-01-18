"""
Copyright 2017 Troy Hirni
This file is part of the pyro project, distributed under the terms 
of the GNU Affero General Public License.

DATA - Support for the data package.
"""


from .. import *



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
	
	# set an external object's item value.
	def setkv(self, obj, key, value):
		"""
		Set the value associated with the given object's key. This is
		meant to facilitate population of lists, dicts, etc... that are
		in the global scope.
		
		x = ff.wrap([['a',1],['b',2]])
		d = {}
		x.each(lambda p: p.setkv(d, p.v[0], p.v[1]))
		print (d)
		"""
		obj[key] = value
	
	
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





class Chain(object):
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
	
	
	# DICT-ONLY
	
	# set a default key value...
	def df(self, k, default):
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
				for i in self.v:
					if not (i in a):
						rr.append(self.v[i])
				self.v = rr
		except KeyError as ex:
			raise type(ex)('error', xdata(i=i,a=a,python=str(ex)))
		except IndexError as ex:
			raise type(ex)('error', xdata(i=i,a=a,python=str(ex)))
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
	
	
	# GENERAL
	def do(self, fn):
		self.v = fn(self.v)

