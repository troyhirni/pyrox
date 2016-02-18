"""
Copyright 2014-2016 Troy Hirni
This file is part of the pyro project, distributed under
the terms of the GNU Affero General Public License.

CORE - Basic Application Components

Defines the central component of a pyro(x)-based application. It 
will define base classes that support processor time sharing and
uninterrupted runtime reload, as well as services that constitute
an application. 
"""

try:
	import thread
except:
	import _thread as thread 

try:
	from .. import base   # to import cross-version types
	from ..base import *  # for clarity in function calls
except:
	import base
	from base import *

from . import _core

import time, weakref


DEF_SLEEP = 0.1



def coreload():
	"""Convenience function, to coreload from interpreter."""
	Core.coreload()




class Core(_core.Core):
	pass




class CoreBase(object):
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
			self.__paused = False # needed only by root object
		
	
	
	# DECORE
	def _decore(self):
		"""
		Store this object's information for restoration after coreload.
		
		The inherrited _decore() must be called first in every subclass
		_decore() method. Use the dict this method returns to record all
		information to rebuild this object's state after coreload.
		
		Note that the paused state is set here as an indicator that no 
		processing should take place while this object is "decored".
		"""
		self.root.__paused = True
		return {
			'type' : base.typestr(self),
			'args' : self.__args,
			'kwargs' : self.__kwargs, 
			'core' : {}
		}
	
	
	# ENCORE
	def _encore(self, d):
		"""
		Subclasses should override the _encore() method to reset a new
		instance of this object to it's state prior to coreload.
		
		Note: This method removes the pause state, so it should be the
		      last method called before returning this object to an
		      active state.
		"""
		self.root.__paused = False
	
	
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
	
	
	@property
	def paused(self):
		"""
		Convenience method for debugging after coreload() errors. This
		method should always return False during normal operation.
		"""
		return self.root.__paused
	
	
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







class CoreNode(CoreBase):
	
	def __init__(self, config=None, **kwargs):
		conf = self.config(config, **kwargs)
		CoreBase.__init__(self)
		
		if self.root == self.proxy:
			self.__rsleep = conf.get('rsleep', DEF_SLEEP)
		else:
			self.__rsleep = None
		
		self.__sleep = conf.get('sleep', DEF_SLEEP) #0.1
		self.__active = False
		self.__running = False
		self.__threaded = False
	
	
	def __del__(self):
		"""Stop/close this object."""
		try:
			self.shutdown()
		except:
			pass
	
	
	def _decore(self):
		"""Store runtime data in preparation for coreload."""
		dd = CoreBase._decore(self)
		me = dd['core']['CoreNode'] = {}
		with thread.allocate_lock():
			
			# save state data
			me['active'] = self.active
			me['running'] = self.running
			me['threaded'] = self.threaded
			me['rsleep'] = self.__rsleep
			me['sleep'] = self.sleep
			
			# stop the main loop
			if self.running:
				self.stop()
			
			# Set active False; DO NOT close() or connections will be lost.
			self.__active = False
		return dd
	
	
	def _encore(self, data):
		"""Restore runtime data after coreload."""
		
		me = data.get('core',{}).get('CoreNode',{})
		self.__sleep = me.get('sleep')
		self.__rsleep = me.get('rsleep')
		self.__active = me.get('active')
		
		CoreBase._encore(self, data)
		
		if (not self.threaded) and me.get('threaded'):
			self.start()
		
		#
		# CRITICAL:
		#  - After a coreload() on a system of objects that's running
		#    in a single thread, this is the last stop. Therefore, any
		#    subclass _encore methods must make certain this method is
		#    called last in the chain of calls to parent._encore.
		#
		elif me.get('running'):
			self.run()
	
	@property
	def active(self):
		"""True if this object was opened via the open() method."""
		return self.__active

	@property
	def running(self):
		"""True if operational via the run() or start() method."""
		return self.__running

	@property
	def threaded(self):
		"""True if this object is threaded via the start() method."""
		return self.__threaded
	
	@property
	def sleep(self):
		"""
		The time to sleep after a pass through the io() method. Only 
		applies if this object is threaded.
		"""
		return self.__sleep
	
	@sleep.setter
	def sleep(self, fSleepTime):
		self.__sleep = fSleepTime
	
	@property
	def rsleep(self):
		"""
		The time to sleep after a pass through the io() method. Only 
		applicable if this object is the root object and is NOT threaded.
		"""
		return self.__rsleep
	
	@rsleep.setter
	def rsleep(self, fSleepTime):
		if self.root != self.proxy:
			raise ValueError('core-rsleep-root-only')
		self.__rsleep = fSleepTime
	
	
	#
	# OPERATIONAL METHODS
	#
	
	def open(self, *args, **kwargs):
		"""
		Open this object. Extended by subclasses that need to open
		connections or otherwise prepare for normal operation.
		"""
		#if not self.__active:
		#	self.sensor.open()
		self.__active = True
	
	
	def run(self, *args, **kwargs):
		"""
		Run this object in the current thread. Control does not return 
		until the object stops running. If not already active (open),
		args and kwargs are passed to the open method before running.
		"""
		if self.running:
			raise Exception("core-already-running")
		try:
			if not self.active:
				self.open(*args, **kwargs)
			
			self.__running = True
			
			# THE RUN LOOP
			while self.running:
				try:
					if self.threaded and self.sleep:
						time.sleep(self.sleep)
					elif self.running and self.__rsleep:
						time.sleep(self.__rsleep)
					if not self.paused:
						self.io()
				except Exception as ex:
					raise #self.onError()
		
		finally:
			self.stop()
	
	
	def io(self):
		"""
		This method is called repeatedly from the run() loop while the 
		object is active.
		"""
		pass
		#self.sensor.io()
	
	
	def stop(self):
		"""Stop running but leave the object in an open state."""
		self.__running = False
		self.__threaded = False
	
	
	def close(self):
		"""
		Closes the object. This is the complement to the open() method, 
		used to tear down connections and other structures only used in
		an active (open) state.
		
		NOTE: Does not affect the 'running' state.
		"""
		if self.__active:
			self.__active = False
			#self.sensor.close()
	
	def start(self, *args, **kwargs):
		"""
		Start this object by calling it's run() method in a new thread, 
		sleep, then returns self.
		"""
		args = args if args else (None,)
		self.__threaded = True
		thread.start_new_thread(self.run, args, kwargs)
		time.sleep(self.sleep)
		return self
	
	
	def shutdown (self):
		"""Close and stop this object."""
		try:
			self.close()
		finally:
			self.stop()
	
