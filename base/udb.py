"""
Copyright 2014-2015 Troy Hirni
This file is part of the pyro project, distributed under
the terms of the GNU Affero General Public License.

UCD - Unicode Data, plus utilitie data and methods.

This module covers the python built-in unicodedata module, with a
few additional methods and properties.
"""


import unicodedata as ucd

try:
	from pyrox.base import *
	#from ..base import *
except:
	from base import *
	


	
# UTILITY
def ucharmap(*args):
	r = []
	for a in args:
		x=[unichr(a)] if isinstance(a,int) else map(unichr,range(*a))
		r.extend(x)
	r.sort()
	return r

def xsafe(fn, *a):
	"""Execute fn with *args. Returns None on error."""
	try:
		return fn(*a)
	except:
		return None

#
# UNICODEDATA MODULE COVER
# Wraps mathods in a function that protects from exceptions.
#
def lookup(c):
	return xsafe(ucd.lookup, c)

def name(c):
	return xsafe(ucd.name, c)

def decimal(c):
	return xsafe(ucd.decimal, c)

def digit(c):
	return xsafe(ucd.digit, c)

def numeric(c):
	return xsafe(ucd.numeric, c)

def category(c):
	return xsafe(ucd.category, c)

def bidirectional(c):
	return xsafe(ucd.bidirectional, c)

def combining(c):
	return xsafe(ucd.combining, c)

def east_asian_width(c):
	return xsafe(ucd.east_asian_width, c)

def mirrored(c):
	return xsafe(ucd.mirrored, c)

def decomposition(c):
	return xsafe(ucd.decomposition, c)

def normalize(form, unistr):
	return xsafe(ucd.normalize, form, unistr)


class PropList(object):
	"""
	This was my first idea, but now I'm rethinking. These would as be
	better-done in normal DEFINE-style, but extracted from a UCD.zip 
	file on module-load. 
	"""
	
	# PROPERTY LIST MEMBERS
	@classmethod
	def whitespace(cls):
		"""
		ftp://www.unicode.org/Public/UCD/latest/ucd/PropList.txt
		0009..000D ; White_Space # Cc  [5] <control-0009>..<control-000D>
		0020       ; White_Space # Zs      SPACE
		0085       ; White_Space # Cc      <control-0085>
		00A0       ; White_Space # Zs      NO-BREAK SPACE
		1680       ; White_Space # Zs      OGHAM SPACE MARK
		2000..200A ; White_Space # Zs [11] EN QUAD..HAIR SPACE
		2028       ; White_Space # Zl      LINE SEPARATOR
		2029       ; White_Space # Zp      PARAGRAPH SEPARATOR
		202F       ; White_Space # Zs      NARROW NO-BREAK SPACE
		205F       ; White_Space # Zs      MEDIUM MATHEMATICAL SPACE
		3000       ; White_Space # Zs      IDEOGRAPHIC SPACE
		"""
		try:
			return cls.__WHITESPACE
		except:
			ws = ucharmap((0x0009,0x000D),(0x2000,0x200A),0x0020,
				0x0085,0x00A0,0x1680,0x2028,0x2029,0x2029,0x202F,0x205F,
				0x3000
				)
			cls.__WHITESPACE = ws
			return cls.__WHITESPACE


