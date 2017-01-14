"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyro project, distributed under
the terms of the GNU Affero General Public License.

SCAN TEXT/BYTES

Scan text based on extensive unicode data.
"""

from .. import *
import unicodedata as ucd 




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


def scantext(x, **k):
	"""
	Returns a ScanText if at all possible, else raises an exception.
	"""
	if not isinstance(x, unicode):
		e = {}
		if 'encoding' in k:
			e['encoding'] = k['encoding']
		x = x.decode(**e)
	return ScanText(TextRef(x, **k))




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
		Return -1 if no match is found. Otherwise, returns distance to
		the found item.
		"""
		start = pos = self.pos
		
		# Try to match
		tests = list(a)
		while tests:
			try:
				for x in tests:
					if self.data.match(x, pos):
						return pos-start
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
			self.move(r)
		return r >= 0



class ScanText (Scanner):
	
	#def __init__(self, dataref, pos=0, **k):
	#	ScanText.__init__(self, dataref, pos, **k)
	
	@property
	def proplist(self):
		return udata.PropList
	
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
		ws = self.proplist('White_Space')
		while ws.match(self.cur):
			self.next()
	
	
	def slice(self, length=None, **k):
		"""
		Return a ScanSlice from the current position to a point to be
		determined by given arguments. If length is given, that's the
		exact amount. 
		
		If a seek kwarg is given, seek forward for the next occurance,
		and return a slice of that length.
		
		If seek fails and prop and/or cat kwargs are given, seek through
		any following characters matching any property or category they
		specify and return a slice length.
		
		Otherwise, returns None.
		"""
		if length:
			s = ScanSlice(self.data, self.pos, length)
			self.move(length)
			return s
		
		# try find
		if 'seek' in k:
			length = self.find(k['seek'])
			if length > 0:
				s = ScanSlice(self.data, self.pos, length)
				self.move(length)
				return s
				
		# last resort:
		prop = self.proplist(k['prop']) if 'prop' in k else ''
		cats = k['cat'] if 'cat' in k else ''
		pos = self.pos
		c = self.cur
		while ucd.category(c) or prop.match(c):
			c = self.next()
			length += 1
		
		if length:
			return ScanSlice(self.data, pos, length) #NOTE: saved pos





class ScanSlice (object):
	def __init__(self, ref, startpos, length):
		self.__ref = ref
		self.__pos = startpos
		self.__len = length
		self.__end = self.__pos + self.__len
	
	
	def __str__(self):
		return self.__ref[self.__pos:self.__end]
	
	def __unicode__(self):
		return self.__ref[self.__pos:self.__end]
	
	def __getitem__(self, i):
		if key >= self.__len:
			raise IndexError()
		return self.__ref.data[self.__pos+i]

