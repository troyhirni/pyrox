"""
Copyright 2014-2016 Troy Hirni
This file is part of the pyro project, distributed under
the terms of the GNU Affero General Public License.

Uninterrupted runtime reload support for core-contained objects.
"""

try:
	from .. import base
except:
	import base

try:
	reload
except:
	from imp import reload

import weakref



# ON-CORELOAD
def oncoreload():
	"""
	Reloads all base and core modules; Tries to import and reload a
	_coreload module in the parent directory (if one exists).
	Alternately, you can replace this oncoreload() function with your 
	own reloading function for tighter control of what gets reloaded.
	"""
	try:
		from ..base import _coreload as base_coreload
	except:
		import base._coreload as base_coreload
	reload(base_coreload)
	
	from . import _coreload
	reload(_coreload)
	reload(base)
	
	try:
		from .. import _coreload as _parent_coreload
	except:
		pass
	else:
		reload(_parent_coreload)




#
# CORE
#
class Core(object):
	__CORES = []
	def __init__(self, *a, **k):
		"""
		Pass args and kwargs necessary for a Factory to create the
		object to be contained by this core. Ths can be a config file
		path.
		"""
		k['core'] = self.proxy
		self.__r = base.create(*a, **k)
		self.__p = weakref.proxy(self.__r)
		Core.__CORES.append(self)
	
	def __del__(self):
		if self in Core.__CORES:
			Core.__CORES.remove(self)
	
	def __call__(self):
		return self.__p
	
	@property
	def proxy(self):
		return weakref.proxy(self)
	
	@classmethod
	def cores(self):
		return Core.__CORES
	
	@classmethod
	def coreload(cls):
		cd = []
		for c in Core.__CORES:
			cd.append([c, c()._decore()])
		oncoreload()
		for c,d in cd:
			c.reroot(d)
			c()._encore(d)
	
	def reroot(self, d):
		t = d['type']
		a = d['args']
		k = d['kwargs']
		k['core'] = self.proxy
		self.__r = base.create(t, *a, **k)
		self.__p = weakref.proxy(self.__r)


