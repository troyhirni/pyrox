"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyro project, distributed under
the terms of the GNU Affero General Public License.

Uninterrupted runtime reload for supported objects.
"""
try:
	reload
except:
	from imp import reload


from .. import *


import weakref



# ON-CORELOAD
def oncoreload():
	"""
	The ../_coreload.py file must import then reload all modules in the
	project, including any packages above it in the directory structure,
	and all their contained packages and modules. The core._coreload
	module must be called, too.
	"""
	from .. import _coreload as base_coreload
	reload(base_coreload)




#
# CORE
#
class Core(object):
	"""
	Contains one "root" object that must implement a _decore() method  
	which returns all data necessary to rebuild the root object (and 
	any objects it contains) as a dict, and an _encore() method that 
	can rebuild the root and it's contents given that core data dict.
	"""
	__CORES = []
	def __init__(self, *a, **k):
		"""
		Pass args and kwargs necessary for a Factory to create the
		root object to be contained by this core. This can be a config 
		file path or the arguments and kwargs accepted by Base.create(), 
		but cannot be a straight type or core0load() will fail.
		"""
		k['core'] = self.proxy
		self.__r = Base.create(*a, **k)
		self.__p = weakref.proxy(self.__r)
		Core.__CORES.append(self.proxy)
	
	def __del__(self):
		"""Cleans up private static list of cores."""
		for p in Core.__CORES:
			x = Core.__CORES.index(p)
			if x >= 0:
				del(Core.__CORES[x])
	
	def __call__(self):
		"""Return the proxy to this core's root object."""
		return self.__p
	
	@property
	def root(self):
		"""Return the proxy to this core's root object."""
		return self.__p
	
	@property
	def roottype(self):
		"""The type of the root object."""
		return type(self.__r)
	
	@property
	def proxy(self):
		"""Proxy to this Core object."""
		return weakref.proxy(self)
	
	@classmethod
	def coreload(cls):
		cd = []
		for c in Core.__CORES:
			cd.append([c, c()._decore()])
		oncoreload()
		for c,d in cd:
			c.reroot(d)
			
			# POTENTIALLY CRITICAL!
			# This must be the last thing called in the coreload process
			# so that when the core's root object is running unthreaded it
			# can restart from the run() at the end of the root object's
			# _encore() if necessary.
			c()._encore(d)
	
	
	def reroot(self, d):
		"""Recreate this Core's root object."""
		t = d['type']
		a = d['args']
		k = d['kwargs']
		k['core'] = self.proxy
		self.__r = Base.create(t, *a, **k)
		self.__p = weakref.proxy(self.__r)


