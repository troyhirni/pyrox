"""
Copyright 2014-2016 Troy Hirni
This file is part of the pyro project, distributed under
the terms of the GNU Affero General Public License.

CORE - Basic Application Components  **  UNDER CONSTRUCTION  **

This is the central component of a pyro(x)-based application. It 
will define base classes that support processor time sharing and
uninterrupted runtime reload, as well as services that constitute
an application. 
"""

try:
	from .. import base
	from ..base import *
except:
	import base
	from base import *

from . import _core

import weakref



def coreload():
	"""Convenience method, to coreload from interpreter."""
	Core.coreload()



#
# CORE
#
class Core(_core.Core):
	pass



#
# OBJECT
#
class Object(object):
	"""
	Basic core object; contains methods and properties needed to exist
	in a system of core objects.
	"""
	
	def __init__(self, config=None, *args, **kwargs):
		
		# CONFIG
		conf = self.config(config, *args, **kwargs)
		
		# CORE (specified only for root object)
		c = conf.get('core')
		if c:
			self.__core = proxify(c)
			del(conf['core'])
	
		# OWNER (specified for all objects except root)
		o = conf.get('owner')
		if o:
			self.__owner = proxify(o)
			del(conf['owner'])
		else:
			self.__owner = None
	
	
	# DECORE
	def _decore(self):
		return {
			'type' : typestr(self),
			'args' : self.__args,
			'kwargs' : self.__kwargs, 
			'core' : {
				'Object' : {}
			}
		}
	
	
	# ENCORE
	def _encore(self, d):
		pass
	
	
	@property
	def core(self):
		"""
		Finds (if necessary) and returns the proxy to
		the core object.
		
		NOTE: The core object (of class Core) contains
		      the root object but should not be considered
		      as being a part of the object tree.
		"""
		try:
			return self.__core
		except Exception:
			r = self.root
			#self.__core = r.core if r else None #<--RECURSIION LOOP!
			self.__core = r.core if (r and self.owner) else None
			return self.__core
	
	
	@property
	def owner(self):
		"""
		Returns a proxy to this object's owner.
		"""
		return self.__owner
	
	
	@property
	def proxy(self):
		"""
		Returns this object's proxy.
		"""
		try:
			return self.__proxy
		except:
			self.__proxy = weakref.proxy(self)
			return self.__proxy
	
	
	@property
	def root(self):
		"""
		Returns the root object's proxy.
		
		WARNING: The root object DOES return a proxy 
		to itself, which could lead to infinite loops
		if used incorrectly.
		"""
		try:
			return self.__root
		except Exception:
			if self.__owner:
				self.__root = self.__owner.root
			else:
				self.__root = self.proxy
		return self.__root
	
	
	# CONFIG
	def config(self, *args, **kwargs):
		"""
		Returns the configuration dict for this object. First call fully
		instantiates and stores this object's configuration. Subsequent 
		calls will return the stored config.
		"""
		try:
			return self.__conf
		except Exception:
			pass
		
		config = args[0] if len(args) else {}
		
		# Store args/kwargs for _decore
		self.__args = args
		self.__kwargs = kwargs
		
		if isinstance(config, (str,unicode)):
			path = util.expandpath(config, checkpath=False)
			if os.path.exists(path):
				config = base.config(path)
		
		if not isinstance(config, dict):
			config = {}
		
		# Kwargs always replace config values.
		config.update(kwargs)
		
		# store config and return it
		self.__conf = config
		return self.__conf


