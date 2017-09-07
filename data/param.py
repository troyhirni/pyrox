"""
Copyright 2017 Troy Hirni
This file is part of the pyro project, distributed under the terms 
of the GNU Affero General Public License.

PARAM - Support for the data package.

The Param class defined in this module is intended to facilitate the
use of lambda callbacks for selection and manipulation of data being
imported and processed by data.cursor.Cursor class objects. The Chain
class is the base for param, providing a set of methods for altering
a param object's value. Param's methods are more about assessment.
	
NOTES:
 * The brief method-naming of class methods defined in this module
   is intended to facilitate a lot of action in a very small space. 
   This is helpful when writing lambda functions, but it may take 
   some time to get the hang of it.
 * The previous contents of this module have been moved back to the 
   pdq module, thier only user. Eventually I hope to upgrade pdq to 
   work with Cursors, these Param objects, and Chains (or whatever 
   replaces them... I'm not too sure I like the name).

EXPERIMENTAL. This module is a work in progress. I'm looking for the
              best way to work with callback methods - in particular,
              lambdas - when querying streams from particularly large
              files or data structures, so I need the best possible
              speed and ease of use. It seems that every time I think
              I've got it settled, a better idea comes to me, so...
              
              *Expect frequent, possibly sweeping changes here!*
"""             


from . import *


class Chain(object):
	"""
	The Chain object carries a value and its methods manipulate that 
	value. Chain methods *ALWAYS* return self (though their subclasses
	may not). Some chain methods exist only so that they can perform an 
	operation and then append another operation afterward; that's why 
	it's called 'Chain'... because you can "chain" the operations - an
	important feature when used inside lambdas. 
	
	REMEMBER:
	 * methods always return self; I won't mention it in doc comments
	 * all methods manipulate the internal value, self.v
	 * chain object's .v always holds their current value
	
	EXCEPTION:
	The only exception to the 'returns self' rule is the __call__()
	method, which returns a new object of type(self), passing any given
	arguments along to the constructor.
	"""
	def __init__(self, v=None):
		self.v = v
	
	def __call__(self, *a):
		return type(self)(*a)
	
	def proc(self, fn, *a, **k):
		"""
		Set this object's self.v to the result of the callable argument
		`fn`. All args and kwargs are passed on to the callable.
		
		Use this when you want to set self.v to the callable's result.
		"""
		self.v = fn(*a, **k)
		return self
	
	def set(self, v):
		self.v = v
		return self
	
	def split(self, *a, **k):
		"""
		Split this value by the string given as the first argument, or
		by the default, if no arguments are given. Keyword args will be
		applied to the str.split() method.
		"""
		self.v = self.v.split(*a, **k)
		return self
	
	def join(self, c, *a, **k):
		"""
		EXPERIMENTAL
		
		Join list items by character `c`. If no additional arguments are
		given, all items in list `self.v` are joined. If additional args
		are given, they must be integers that give offsets from self.v to 
		join.
		
		NOTE: All list values are cast as unicode before being joined.
		"""
		x = self.v
		u = unicode
		vv =  [u(x[i], **k) for i in a] if a else [u(v, **k) for v in x]
		self.v = u(c, **k).join(vv)
		return self



class Param(Chain):
	"""
	Param methods manipulate or evaluate data; usually the self.v value
	is involved. All methods work with either self.v, or in some cases,
	an optional second argument to use instead of self.v.
	
	Comparison methods eq, neq, gt, ge, lt, and le all require one
	argument and accept an optional second argument (which defaults to
	self.v).
	
	Methods inherrited from Chain always return `self`, so that calls 
	can be chained through a lambda, whereas Param methods typically, 
	if not always, return valaue resulting from the method. It may take
	a while to what you're getting back as you chain calls together, 
	but once you get it, it's a powerful tool for use in lambdas.
	"""
	def __init__(self, v=None, i=None):
		self.v = v
		self.i = i
	
	def __getitem__(self, key):
		return self.v[key]
	
	def __str__(self):
		return str(self.v)
	
	def __unicode__(self):
		try:
			return unicode(self.v)
		except:
			return self.v.decode(DEF_ENCODE)
	
	@property
	def type(self):
		"""Return the type of the current value."""
		return type(self.v)
	
	@property
	def len(self):
		"""Return the length of the current value."""
		return len(self.v)
	
	@property
	def re(self):
		try:
			return self.__re
		except:
			self.__re = __import__('re')
			return self.__re
	
	# COMPARISON
	def eq(self, v, *a):
		"""
		Comparison: Return True if comparison value `v` == self.v; if an  
		optional second argument is given, compares to that instead.
		"""
		return v == (a[0] if a else self.v)
	
	def ge(self, v, *a):
		"""Comparison: greater than/equal to;"""
		return v >= (a[0] if a else self.v)
	
	def gt(self, v, *a):
		"""Comparison: greater than;"""
		return v > (a[0] if a else self.v)
	
	def le(self, v, *a):
		"""Comparison: less than/equal to;"""
		return v <= (a[0] if a else self.v)
	
	def lt(self, v, *a):
		"""Comparison: less than;"""
		return v < (a[0] if a else self.v)
	
	@property
	def true(self):
		return True
	
	@property
	def false(self):
		return False
	
	
	
	def fn(self, fn, *a, **k):
		"""
		Return the result of the callable argument `fn`. All args and 
		kwargs are passed on to the callable.
		
		Use this when you want to return a function result rather than
		setting self.v to the result.
		"""
		return fn(*a, **k)
