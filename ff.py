"""
FAST-FORWARD - DEMO - Coding in the style of jQuery

The fast-forward module's objects encapsulate data in a way similar
to base.pdq Query objects. Most properties and methods return another
ff.FastForward object. 

import ff
d = ff.fdir('.')
d.ls()       # returns flist object
d.ls().val() # returns a python list (directory listing)
d.ls().o     # shorthand - returns .val()

# print each item on its own line
d.ls().each(lambda o: o.out(o.v))

NOTE: This is a very early ff version; As with everything in the
      pyrox project, future versions may be VERY different.
"""

from pyrox import base


def ff(*a, **k):
	"""
	Convenience function that returns common ff objects.
	"""
	if 'file' in k:
		return ffile(k['file'], **k)
	elif 'dir' in k:
		return fdir(k['dir'], **k)
	elif 'list' in k:
		return flist(k['list'])
	elif a:
		x = a[0]
		if isinstance(x, list):
			return flist(x)
		elif isinstance(x, basestring):
			import os
			if os.path.isfile(x):
				return ffile(s, **k)
			elif os.path.isdir(x):
				return fdir(x, **k)
		
	raise Exception('Unknown FastForward Type')





class fparam(object):
	"""
	Parameter object used as argument to lambda calls in methods such
	as each(); Similar to pyrox.base.pdq.QRow.
	
	A new fparam is created for each call to a callback function, and 
	always contains the following member variables:
	
	The fparam member variables are:
	 c : The calling object (eg, an flist)
	 i : The enumerated item number
	 v : The value of the current item
	
	NOTE: The properties are abbreviated as a convenience for use in
	      the very tight space of lambda calls.
	"""
	def __init__(self, caller, item, value):
		self.c = caller # the ff object (not its data)
		self.i = item   # enumerated item's number
		self.v = value  # the actual value of the item
	
	def set(self, value):
		self.v = value
	
	# print output
	def out(self, x):
		"""Print the given value."""
		print(x)
	


# 
# FF - FastForward base class
#
class FastForward(object):
	"""
	Base class receives and stores an initial value
	"""
	def __init__(self, obj, **k):
		self.val(obj, **k)
	
	@property
	def type(self):
		return self.__T
	
	@property
	def o(self):
		return self.__o
	
	def val(self, *a, **k):
		if a:
			x=a[0]
			self.__T = k.get('type', type(x))
			self.__o = x
		else:
			return self.__o
	
	def each(self, fn, *a, **k):
		fn(fparam(self, 0, self.o), *a, **k)
	
	def pdq(self, *a, **k):
		return base.create('pyrox.base.pdq.Query', self.o)




class fdata(FastForward):
	
	def __getitem__(self, key):
		return self.o[key]
	
	def __len__(self):
		return len(self.o)





class ftext(fdata):
	def splitlines(self):
		return flist(self.o.splitlines())
	def dom(self):
		return fdom(self.o)




class flist(fdata):
	
	def __getitem__(self, key):
		return self.o[key]
	
	def __len__(self):
		return len(self.o)
	
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
			fn(fparam(self.o, i, v), *a, **k)
	
	def sort(self, *a, **k):
		"""Sort this list."""
		self.val(sorted(self.o, *a, **k))
		return self
	
	def reverse(self):
		"""Reverse this list."""
		self.val(list(reversed(self.o)))
		return self
	
	def sorted(self, *a, **k):
		"""Return a sorted copy of this list."""
		return flist(sorted(self.o, *a, **k))
	
	def reversed(self):
		"""Return a reversed copy of this list."""
		return flist(reversed(self.o))






class fdom(fdata):
	def __init__(self, text):
		hparse = base.create('pyrox.base.dom.Parse', text)
		fdata.__init__(self, hparse.doc)
	
	




#
# FILE SYSTEM
#

class ffs(FastForward):
	"""File system object."""
	def parent(self):
		return fdir(self.o.path)





class ffile(ffs):
	"""
	File object; Usage notes:
	 * Use self.o to access data directly as a base.fs.File object
	 * Use self.lines to get a list of lines from a text file
	 * Use self.pdq to get a base.pdq.Query loaded with the text from
	   this file.
	"""
	def __init__(self, path, **k):
		ffs.__init__(
			self, base.create('pyrox.base.fs.File', path, **k)
		)
	
	def text(self, mode='r', **k):
		return ftext(self.o.read(mode, **k))
	
	def lines(self, mode='r', **k):
		return flist(self.o.read(mode, **k).splitlines())
	
	def pdq(self, mode='r', **k):
		"""
		Returns a Query object from pyrox.base.pdq
		"""
		return base.create(
			'pyrox.base.pdq.Query', self.o.read(mode, **k)
			)





class fdir(ffs):
	"""Directory object."""
	def __init__(self, path=".", **k):
		ffs.__init__(self, 
			base.create('pyrox.base.fs.Dir', path, **k)
		)
	
	def pdq(self, path, *a, **k):
		return ffile(path, **k).pdq(*a, **k)
	
	def cd(self, *a, **k):
		self.o.cd(*a, **k)
		return self
	
	def mkdir(self, *a, **k):
		self.o.mkdir(*a, **k)
		return self
	
	def head(self, *a, **k):
		return flist(self.o.head(*a, **k))
	
	def read(self, *a, **k):
		return flist(self.o.read(*a, **k))
	
	def file(self, *a, **k):
		return ffile(self.o.file(*a, **k))
	
	def cp(self, *a, **k):
		self.o.cp(*a, **k)
		return self
	
	def mv(self, *a, **k):
		self.o.mv(*a, **k)
		return self
	
	def rm(self, *a, **k):
		self.o.rm(*a, **k)
		return self
	
	def match(self, *a, **k):
		return flist(self.o.match(*a, **k))
	
	def find(self, *a, **k):
		return flist(self.val().find(*a, **k))
		
	def ls(self, *a, **k):
		"""Get flist listing of current directory."""
		return flist(self.val().ls(*a, **k))



