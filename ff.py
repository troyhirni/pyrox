"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyro project, distributed under the terms 
of the GNU Affero General Public License.

FAST-FORWARD - DEMO - Coding in the style of jQuery

FF wraps objects in FFWrapper, pushing them or their results (also
wrapped) forward through a series of chained commands in a way that's
similar to data.pdq.Query objects.

"""


def wrap(o):
	"""
	Argument `o` is an object
	"""
	if isinstance(o, list):
		return FFList(o)
	return FFWrapper(o)





class FFSetter(object):
	"""
	Stores a FastForward object and an executable attribute. When the
	stored attribute is called, it's result is wrapped in an FF object
	and stored as the (stored) object's value.
	"""
	def __init__(self, wrapper, attr):
		self.__wrap = wrapper # an FFWrapper object
		self.__attr = attr    # an executable value
	
	def __call__(self, *a, **k):
		"""
		When this setter is "called", the stored attribute's result is 
		'wrapped' using the wrap() function and the result is set as the
		stored object's value.
		"""
		o = self.__attr(*a, **k)
		self.__wrap.o = o
		if isinstance(o, list):
			return wrap(o)





class FF(object):
	
	def __init__(self, o):
		self.__o = o
	
	@property
	def o(self):
		"""
		Return the wrapped object, whether from FFWrapper or FFData
		subclasses.
		"""
		return self.__o
	
	@o.setter
	def o(self, o):
		self.__o = o





class FFWrapper (FF):
	"""
	Copies an object's attributes, wrapping them inside an FFSetter
	object that sets this object's value to an FF subclass object
	containing the attribute method's result.
	"""
	def __init__(self, o, *a, **k):
		"""
		Pass object `x`; this object will be "wrapped" - it's attributes
		copied to this FFWrapper object, but wrapped in an FFWrapper that
		stores the original objects method results as FF subclass values.
		"""
		FF.__init__(self, o)
		for n in dir(self.o):
			if not ("__" in n):
				ax = getattr(self.o, n)
				if type(ax).__name__ == 'instancemethod':
					setattr(self, n, FFSetter(self, ax))





class FFParam(object):
	"""
	Parameter object used as argument to lambda calls in methods such
	as each(); Similar to pyrox.base.pdq.QRow.
	
	A new fparam is created for each call to a callback function, and 
	always contains the following member variables:
	
	The fparam member variables are:
	 c : The calling object (eg, an FFList)
	 i : The enumerated item number
	 v : The value of the current item
	
	NOTE: The properties are abbreviated as a convenience for use in
	      the very tight space of lambda calls.
	"""
	def __init__(self, caller, item, value):
		self.c = caller # the ff object (not its data)
		self.i = item   # enumerated item's number
		self.v = value  # the actual value of the item
		
		# the caller's contained object... for brevity's sake
		self.o = self.c.o
	
	def set(self, value):
		"""
		Set the entire value of the current item.
		"""
		self.c.o = value
		return self
	
	def seti(self, i, value):
		"""
		Set the item value of the current item. For example, if caller
		self.c is a list, set self.c[i]=value.
		"""
		self.c.o[i] = value
		return self
	
	# print output
	def out(self, x):
		"""Print the given value."""
		print(x)
		return self





class FFData(FF):
	"""
	Base class for builtin python classes such as list, str, etc...
	"""
	def __getitem__(self, key):
		return self.o[key]
	
	def __len__(self):
		return len(self.o)





class FFSeriesData(FFData):
	def each(self, fn, *a, **k):
		"""
		Execute the given function once for each item in this list. The
		function receives an fparam object with the following members:
		 o : this object
		 i : the enumerated integer value of the current item
		 v : the value of the current item
		
		Any additional arguments or keyword args are appended to the 
		function's args and/or kwargs (so be sure to catch them if you
		pass them).
		"""
		for i,v in enumerate(self.o):
			fn(FFParam(self, i, v), *a, **k) 
		return self





class FFList(FFSeriesData):
	
	def sort(self, *a, **k):
		"""
		Sort this list by passing self.o to the built-in `sorted` method.
		Any additional args and kwargs are passed along to sorted().
		"""
		self.o = sorted(self.o, *a, **k)
		return self
	
	def reverse(self):
		"""Reverse this list."""
		self.o = list(reversed(self.o))
		return self
	
	def sorted(self, *a, **k):
		"""
		Return a sorted copy of this list. Any additional args and kwargs
		are passed along to sorted().
		"""
		return FFList(sorted(self.o, *a, **k))
	
	def reversed(self):
		"""Return a reversed copy of this list."""
		return FFList(list(reversed(self.o)))


