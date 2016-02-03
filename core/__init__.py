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
	from .. import base   # to import cross-version types
	from ..base import *  # for clarity in function calls
except:
	import base
	from base import *

from . import _core

import weakref



def coreload():
	"""Convenience function, to coreload from interpreter."""
	Core.coreload()




class Core(_core.Core):
	pass





class CoreNode(object):
	"""
	The base class for core package objects; contains methods and 
	properties that link the object within a tree structure.
	"""
	
	def __init__(self, config=None, *args, **kwargs):
		
		# CONFIG
		conf = self.config(config, *args, **kwargs)
		
		# CORE (specified only for root object)
		c = conf.get('core')
		if c:
			self.__core = base.proxify(c)
			del(conf['core'])
	
		# OWNER (specified for all objects except root)
		o = conf.get('owner')
		if o:
			self.__owner = base.proxify(o)
			del(conf['owner'])
		else:
			self.__owner = None
	
	
	# DECORE
	def _decore(self):
		return {
			'type' : base.typestr(self),
			'args' : self.__args,
			'kwargs' : self.__kwargs, 
			'core' : {}
		}
	
	
	# ENCORE
	def _encore(self, d):
		pass
	
	
	@property
	def core(self):
		"""
		Find (if necessary) and return the proxy to the core object.
		NOTE: The core object (Core) contains the root object but should
		      not be considered as being a part of the object tree.
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
		"""Return a proxy to this object's owner."""
		return self.__owner
	
	
	@property
	def proxy(self):
		"""Return this object's proxy."""
		try:
			return self.__proxy
		except:
			self.__proxy = weakref.proxy(self)
			return self.__proxy
	
	
	@property
	def root(self):
		"""
		Return a proxy to the root object of this object's tree.
		WARNING: The root object DOES return a proxy to itself, which 
		         could lead to infinite loops if used incorrectly.
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
		Return the configuration dict for this object. First call fully
		instantiates and stores this object's configuration. Subsequent 
		calls return the stored config.
		"""
		try:
			return self.__conf
		
		except Exception:
			config = args[0] if len(args) else {}
			
			# Store args/kwargs for _decore
			self.__args = args
			self.__kwargs = kwargs
			
			if isinstance(config, basestring):
				path = base.Path.expand(config, checkpath=False)
				if os.path.exists(path):
					config = base.config(path)
			
			if not isinstance(config, dict):
				config = {}
			
			# Kwargs always replace config values.
			config.update(kwargs)
			
			# store config and return it
			self.__conf = config
			return self.__conf


