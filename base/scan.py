"""
Copyright 2014-2016 Troy Hirni
This file is part of the pyro project, distributed under
the terms of the GNU Affero General Public License.

SCAN TEXT/BYTES




"""


import unicodedata as ucd 

try:
	from ..base import *
except:
	from base import *

from . import udata



def scan(x, **k):
	"""
	Returns a scanner appropriate to arguments. Arg 'x' may be a byte
	or unicode text string. If encoding is included with bytes, the
	bytes will be decoded and the Scanner will work with unicode text.
	
	Whether scanning bytes or unicode text, Scanner method arguments
	must be passed as the corresponding type.
	"""
	ub = isinstance(x, unicode)
	if ub or ('encoding' in k):
		if not ub:
			x = x.decode(k['encoding'])
		return ScanText(TextRef(x, **k))
	return Scanner(DataRef(x))




class DataRef(object):
	def __init__(self, data):
		self.data = data
		self.__len = len(data)
	
	@property
	def length(self):
		return self.__len
	
	def __getitem__(self, key):
		return self.data[key]
	
	def __len__(self):
		return self.__len
	
	def match(self, test, pos):
		"""
		Return True if test matches the data starting at pos, else 
		raises IndexError when data is exhausted.
		"""
		cur = pos
		for x in test:
			if not self.data[cur] == x:
				return False
			cur += 1
		return True




class TextRef(DataRef):
	def __init__(self, data, **k):
		DataRef.__init__(self, data)
		self.__enc = k.get('encoding')
	
	@property
	def encoding(self):
		return self.__enc
	
	def cat(self, pos):
		"""Return unicode category of current codepoint."""
		return ucd.category(self.data[pos])




class Scanner(object):
	def __init__(self, dr, pos=0, **k):
		self.__k = k
		self.__data = dr if isinstance(dr, DataRef) else DataRef(dr, **k)
		self.__pos = pos if pos >= 0 else 0
	
	@property
	def data(self):
		return self.__data
	
	@property
	def cur (self):
		"""Return current byte or codepoint."""
		return self.__data[self.pos]
	
	@property
	def rest(self):
		"""Copy the rest of the data from the current position."""
		return self.__data[self.pos:]
	
	@property
	def pos (self):
		"""Current position in scan."""
		return self.__pos
	
	# GENERAL
	def clone(self):
		"""
		Return a new Scan object set to this object's data and position.
		"""
		return type(self)(self.__data, self.pos, **self.__k)
	
	def move(self, i):
		"""Move by integer i."""
		self.__pos = self.pos + i
	
	def next(self):
		c = self.cur
		self.__pos += 1
		return c
	
	def peek(self):
		"""Returns next character/byte without moving."""
		return self.__data[self.pos + 1]
	
	
	# SEARCH
	def match(self, x):
		"""Return the lenght of x if next data == x, else 0."""
		L = len(x)
		return L if self.__data[self.pos:L] == x else 0
	
	def find(self, *a):
		"""
		Search forward for the first match to any the given arguments. 
		Return None if no match is found. Otherwise, returns a tupel 
		containing
		(
			* the number of bytes ahead the first match is found
		  * the value matched
		)
		
		DOES NOT MOVE! The current position is not changed.
		"""
		start = pos = self.pos
		
		# Try to match
		tests = list(a)
		while tests:
			try:
				for x in tests:
					if self.data.match(x, pos):
						return (pos-start, x)
			except IndexError:
				tests.remove(x)
			pos += 1
	
	
	def seek(self, *a):
		"""
		Seek forward for the first match to any the given arguments. If
		found, moves forward to the first match and returns True. Else,
		returns False.
		"""
		r = self.find(*a)
		if r:
			self.move(r[0])
			return r[1]
			
	
	
	
	
class ScanText (Scanner):
	
	@property
	def cat (self):
		"""Return category for char at current position. (Text only.)"""
		return ucd.category(self.cur)
	
	@property
	def encoding(self):
		return self.__data.encoding
	
	
	def passcat(self, cats):
		"""
		Pass a list of (or space-separated string listing) UCD category 
		codes. Skips forward to the next character that does not match 
		any given 'cats'.
		"""
		cats = cats if isinstance(cats, list) else cats.split()
		if cats:
			while self.data.cat(self.pos) in cats:
				self.next()
	
	def passwhite(self):
		"""Move to the next character with no 'White_Space' property."""
		while udata.hasproperty(self.cur, 'White_Space'):
			self.next()



