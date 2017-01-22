"""
Copyright 2017 Troy Hirni
This file is part of the pyro project, distributed under the terms 
of the GNU Affero General Public License.

CURSOR - Generators or iteration through data of various types.
         Requires: python 2.2+

Cursor objects are for one-time use, to navigate a variious types of
(hopefully any kind of) data. They're intended for internal use, in
support of various other data package modules, but could be useful if
you want a generator for data that comes in a variety of objects.

for item in cursor.Cursor([[1,2,3], [4,5,6]]).gen:
	print (item)
"""

from .. import *

#
# GENERATORS
#  - Generators introduced in 2.2

def genseq(data):
	for v in data:
		yield v
	
def genmap(data):
	for k in data:
		yield data[k]
	
def genlines(data):
	yield data.readline()

def geniter(data):
	try:
		data.__next__
		return geniter3(data)
	except:
		return geniter2(data)

def geniter2(data):
	yield data.next

def geniter3(data):
	yield next(data)
	
def genval(data):
	yield data
		




#
# PARAMS - these probably belong in the param.py module
#
class CursorParam(object):
	def __init__(self, value, *a, **k):
		self.v = value # REM! Don't use an @property - twice as slow
		self.a = a
		self.k = k





#
# CURSOR
#
class Cursor(object):
	"""
	Cursor objects are for one-time iteration through a list, dict, 
	iterators, generators, text or file streams (line by line), or even
	just a single values such as int, float, whatever... (hopefully, at
	least eventually) any kind of data. Cursor will select the correct
	generator to match the data.
	
	Use fetch() or fetchall() to return one or all of the data. Use the
	generator() classmethod to get the generator of an unknown type.
	Call any of the individual gen-prefixed functions directly if you 
	know your object type or, if you prefer, pass a keyword value whose
	key specifies the generator you want (and value specifying the key
	object) to the Cursor constructor (instead of data)
	"""
	
	def __init__(self, data=None, *a, **k):
		"""
		Pass the (optional) data to iterate as `data` argument.
		Alternately, pass a keyword argument with name and value as 
		required by the generator() classmethod.
		
		FETCH:
		This constructor also sets a fetch value that's equal to the 
		generator's `next` method in python 2, or it's `__next__` method
		in python 3. This is done to provide a .fetch() method with the
		greatest possible speed (for iteration through huge datasets).
		
		Example:
		c = cursor.Cursor([1,2,3])
		c.fetch() # returns the next item (or raises StopIteration)
		"""
		
		# create the correct generator for the given data
		self.__gen = self.generator(data, *a, **k)
		
		# steal the generator's 'next' method
		try:
			self.fetch = self.__gen.__next__
		except:
			# for python 2
			self.fetch = self.__gen.next
	
	
	@property
	def gen(self):
		return self.__gen
	
	
	@classmethod
	def gentype(cls, x=None, *a, **k):
		"""
		The generator() method returns a generator based on the type of
		data passed to it.
		"""
		# if it's already a generator, return it
		if (type(x).__name__ == 'generator'):
			return x
		
		# list, dict, and string will probably be the most common types
		# when recursing; unfortunately, they have to come in the wrong
		# order; Maybe I can find a way to improve speed here.
		try:
			x.keys
			x.__getitem__
			return genmap
		except AttributeError:
			pass
		
		# make sure a string isn't thrown in with list, tupel, etc...
		if isinstance(x, basestring):
			return genval
		
		# any sequence that doesn't have keys
		try:
			x.__getitem__
			return genseq
		except AttributeError:
			pass
		
		try:
			if x == x.__iter__():
				return geniter(x)
		except Exception:
			pass
		
		# text input (via file, url, or string) will probably be the most
		# common *FIRST* thing to be cursored over, then yielding a list
		# to parse; in such cases, though, the list is probably a list of
		# lists or dicts which will need to be "recursed", so it might be
		# best file or string io is lower in the list
		try:
			x.readline
			return genlines
		except AttributeError:
			pass
		
		# comment this line to debug when testing for new possible types
		return genval
		
		# TEMP! DEBUGGING!!
		#return type(x)
	
	
	
	@classmethod
	def generator(cls, data=None, **k):
		"""
		The generator classmethod returns the cursor module generator 
		best-suited to the type of data you pass it. 
		
		You can explicitly specify a generator type by leaving out the 
		`data` argument (or by specifying None, its default) and then
		specifying one of these keywords with a value set to the 
		corresponding type of object:
			* lines = a stream (or any object) that implements readline()
			* dict  = any object that implements .keys() and __getitem__()
			* list  = a list, or any object that implements __getitem__()
			* iter  = an iterator
			* gen   = a generator (returns itself)
		
		If you pass kwarg 'value', that value is yeilded from a generator
		as-is, one time. I'm not sure this is useful, but I can't prove
		it's not so I'll leave it for now.
		"""
		if k:
			if 'lines' in k:
				return genlines(k['lines'])
			elif 'list' in k:
				return genseq(k['list'])
			elif 'dict' in k:
				return genseq(k['dict'])
			elif 'iter' in k:
				return geniter(k['iter'])
			elif 'value' in k:
				return genval(k['value'])
			elif 'gen' in k:
				return k['gen']
			
		else:
			gen = cls.gentype(data)
			return gen(data)

