"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

MORPH - Morph one value into another.       ***EXPERIMENTAL***

Create a Morph object by passing a callable object; use the result as
a function. Eg:
>>> add1 = Morph(lambda v: v+1)
>>> add1(2) #returns 3
"""

from .. import *


#
# I'm starting to think this isn't really necesary at all.
#


class Morph(object):
	def __init__(self, fn):
		self.fn = fn
	
	def __call__(self, *a, **k):
		return self.fn(*a, **k)


# JSON
class jsonbase(Morph):
	@classmethod
	def encoder(cls):
		try:
			return cls.TEncoder
		except:
			cls.TEncoder = TFactory('fmt.JSONDisplay').type
			return cls.TEncoder


class json2obj(jsonbase):
	def __init__(self):
		jsonbase.__init__(self, TFactory("json.loads").type)


class obj2json(jsonbase):
	def __init__(self):
		jsonbase.__init__(self, Base.ncreate("fmt.JSON").format)



"""
class Morph(object):
	def __call__(self, value, *a, **k):
		return self.fn(value, *a, **k)


class jsonbase(Morph):
	@classmethod
	def encoder(cls):
		try:
			return cls.TEncoder
		except:
			cls.TEncoder = TFactory('fmt.JSONDisplay').type
			return cls.TEncoder


class json2obj(jsonbase):
	def __init__(self):
		cls.fn = TFactory("json.loads").type
		jsonbase.__init__(self)


class obj2json(jsonbase):
	def __init__(self):
		self.fn = Base.ncreate("fmt.JSON").format
		jsonbase.__init__(self)


class obj2jdisplay(jsonbase):
	def __init__(self):
		self.fn = Base.ncreate("fmt.JDisplay").format
		jsonbase.__init__(self)


class obj2jcompact(jsonbase):
	def __init__(self):
		self.fn = Base.ncreate("fmt.JCompact").format
		jsonbase.__init__(self)
"""