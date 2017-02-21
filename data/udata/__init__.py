"""
Copyright 2015-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

UDATA - Unicode Data

Access to more information from the unicode character database. 



"""

# for root-package definitions (unichr, etc...)
from pyrox import *

import struct, bisect
from .ucdpy.blocks import BLOCKS
from .ucdpy.bidi import BRACKETPAIRS
from .ucdpy.proplist import PROPERTIES

#
# BRACKETS
#

def bracket(c):
	"""
	Return a tuple with 'o' (open) or 'c' (close) indicator and the 
	matching bracket if given character is a bracket, else None.
	
	# EXAMPLE:
	>>> udata.bracket('(')
	('o', u')')
	"""
	i = ord(c)
	x = bisect.bisect_left(BRACKETPAIRS, [i])
	try:
		BP = BRACKETPAIRS[x]
		return (BP[2], unichr(BP[1])) if (BP and BP[0]==i) else None
	except IndexError:
		return None


#
# BLOCKS
#

def block(c):
	"""
	Return block-name for the block containing the given character.
	
	# EXAMPLE:
	>>> udata.block('(')
	'Basic Latin'
	"""
	i = ord(c)+1
	x = bisect.bisect_left(BLOCKS, [[i]])
	B = BLOCKS[x-1]
	return B[1]


#
# PROPERTIES
#

def properties(c):
	"""
	Return a list containing all properties of the given character `c`.
	"""
	r = []
	for k in PropList.keylist():
		if PropList(k).match(c):
			r.append(k)
	return r
	


def proplist(*a, **k):
	"""
	Return a PropList object with the given arguments.
	
	EXAMPLES:
	>>> x = udata.proplist('ASCII_Hex_Digit')
	>>> x.match('a')
	True
	
	>>> # the PropList.keylist class method lists available properties
	>>> udata.PropList.keylist()
	"""
	return PropList(*a, **k)




# UTILITY
def safechr(i):
	"""
	A workaround to prevent ValueError on narrow builds when creating
	characters with a codepoint over 0x10000.
	"""
	try:
		return unichr(i)
	except ValueError:
		return struct.pack('i', i).decode('utf-32') 







class PropList(object):
	
	__KEYS = sorted([k for k in PROPERTIES.keys()])
	__ITEMS = [PROPERTIES[k] for k in __KEYS]
	
	@classmethod
	def __item(cls, key):
		"""Private, to protect __ITEMS from manipulation."""
		return cls.__ITEMS[bisect.bisect_left(cls.__KEYS, key)]
	
	@classmethod
	def keylist(cls):
		"""Returns a copy of __KEYS."""
		return cls.__KEYS[:]
	
	@classmethod
	def indexof(cls, key):
		"""Find index of given key."""
		return bisect.bisect_left(cls.__KEYS, key)
	
	# INIT
	def __init__(self, *a, **k):
		"""
		Pass a list of key strings, or keyword items, a list of integers.
		"""
		ii = k.get('items', [])
		for pname in a:
			if not pname in ii:
				ix = self.indexof(pname)
				if ix < 0:
					raise ValueError('udata-propname-invalid', pname)
				ii.append(ix)
		
		self.__items = ii
		if not self.__items:
			raise ValueError('udata-proplist-empty') #base.xdata()
	
	@property
	def items(self):
		"""Return a list (of integers) this object represents."""
		return self.__items
	
	@property
	def keys(self):
		"""Return a list (of strings) this object represents."""
		try:
			return self.__keys
		except:
			kk = []
			for i in self.__items:
				kk.append(self.__KEYS[i])
			self.__keys = kk
			return self.__keys
	
	
	# MATCH
	def match(self, c):
		"""
		Return True if the given unichr matches one of the properties
		this object was created to represent.
		
		NOTE: This method is sometimes slow depending on the number of
		      comparisons required. Use match() with a PropList object
		      that has the minimum set of keeys that meet your needs.
		"""
		x = ord(c)
		iint = isinstance # 6% faster
		
		# loop through each proplist this object was created to represent
		for listid in self.__items:
			proplist = self.__ITEMS[listid]
			for i in proplist:
				if ((x==i) if iint(i,int) else x>=i[0] and x<=i[1]): # +1%
					return True
		return False
	
	
	# PROP-GEN
	def propgen(self):
		"""
		Return a generator for every character represented by this
		object.
		
		CAUTION: The list could be VERY long, so be careful trying to 
						 copy it.
		"""
		for listid in self.__items:
			proplist = self.__ITEMS[listid]
			for item in proplist:
				if isinstance(item, int):
					yield safechr(item)
				else:
					for x in range(*item):
						yield safechr(x)





if __name__ == '__main__':
	
	import time, sys
	
	# a long string of dfferent unicode characters
	crange = ''.join(map(unichr, range(0x0000, 0xFFFF)))
	bHelp = False
	
	if len(sys.argv) > 1:
		args = sys.argv[1:]
		flag = args[0] if args else ''
		
		# KEYS
		if flag in ['-h', '--help']:
			bHelp = True
		
		# KEYS
		elif flag in ['-k', '--keys']:
			print (PropList.keylist())
		
		# BLOCK
		elif flag in ['-b', '--block']:
			t1 = time.clock()
			for c in crange:
				block(c) 
			t2 = time.clock() - t1
			print (t2)
		
		# BRACKET PAIR
		elif flag in ['-bp', '--bracket']:
			tt = 0.0
			t1 = time.clock()
			for c in crange:
				bracket(c) 
			t2 = time.clock() - t1
			print (t2)
		
		elif flag == '--cat':
			try:
				t = args[1]
			except Exception as ex:
				print ("ERROR: Property Required. Eg, --cat Dash")
			else:
				g = PropList(args[1]).propgen()
				d = {}
				import unicodedata
				for c in g:
					cat = unicodedata.category(c)
					try:
						d[cat] += 1
					except:
						d[cat] = 1 
				#print d
				for x in d:
					print ("%s = %s" % (x, str(d[x])))
		
		# PROP-LIST MATCH
		elif args:
			print ("\nTESTING: "+ ', '.join(args))
			pl = PropList(*args)
			tt = 0.0
			t1 = time.clock()
			for c in crange:
				pl.match(c) 
			t2 = time.clock() - t1
			print (t2)
			print ('')
		
		else:
			bHelp = True
		
	else:
		bHelp = True
	
	
	# PRINT HELP
	if bHelp:
		print ("\nHELP: Performance Testing.")
		print ("Calls a function for each char in (0x0000, 0xFFFF)")
		print (" * Pass a list of properties to test PropList.match()")
		print (" * Use flag -k for a list of PropList keys")
		print (" * Use flag -b or -bp to test block() or bracket()")
		print ("python -m pyrox.data.udata -b\n")

