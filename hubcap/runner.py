"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyro project, distributed under the terms
of the GNU Affero General Public License.

RUNNER - Abstract event loop implementation and support.

Runner is sort-of abstract. It's responsible for repeated calls to
an .io() method, which reads incomming messages and passes them to
an .onMessage() method.
"""


from . import *


# import as 'thread' from python 2 or 3
try:
	import thread
except:
	import _thread as thread



class Runner(Hubcap):
	"""
	Runner implements a virtual event loop that repeatedly calls an 
	io() method which Task and Hub objects must implement to handle
	messaging.
	"""
	
	def __init__(self, config=None, **k):
		"""
		Argument 'config' must be a dict. Keyword arguments will update
		the config dict.
		"""
		conf = config or {}
		conf.update(k)
		self.__sleep = conf.get('sleep', HC_DEF_SLEEP)
		self.__active = None
		self.__running = None
		self.__threaded = None
	
	def __del__(self):
		try:
			self.exit()
		except:
			pass
	
	@property
	def sleep(self):
		"""
		The amount of time to sleep between calls to io()
		"""
		return self.__sleep
	
	@property
	def active(self):
		"""
		True if open() has been called; False after close() has been
		called.
		"""
		return self.__active
	
	@property
	def running(self):
		"""
		True when the object is running - looping through calls to the
		io() method; otherwise; None before run is first called; False
		after stop() has been called.
		"""
		return self.__running
	
	@property
	def threaded(self):
		"""
		True if this object is looping in a thread, else False.
		"""
		return self.__threaded
	
	
	# OPEN
	def open(self):
		"""
		Calls onOpen() to give subclasses a chance to prepare for running
		the event loop, then sets active to True. Raises an Exception
		with message 'open-fail', reason='already-open' if an attempt is
		made to open the object while it's already open.
		
		NOTE: Calling open() sets the 'active' property to True.
		"""
		if self.active:
			raise Exception('open-fail',dict(reason='already-open'))
		self.onOpen()
		self.__active=True
		#self.log("OPEN")
	
	
	# RUN
	def run(self, *a):
		"""
		Loop, processing incomming messages.
		"""
		if self.running:
			raise Exception("run-fail", dict(reason='already-running'))
		
		# force open before running
		if not self.active:
			self.open()
		
		#self.log("RUN")
		self.__running = True
		
		# calling functions as local variables works faster
		io = self.io
		ts = time.sleep
		ss = self.sleep
		
		while self.running:
			try:
				# self.io
				io()
			except Exception as ex:
				self.log(type(ex).__name__, ex.args)
			except BaseException as bx:
				self.log(type(bx).__name__, bx.args)
				self.__running = False
				return 0
			
			# time.sleep(self.sleep)
			ts(ss)
		
		#self.log("RUN-STOP")
		
		time.sleep(1)
		return 0
	
	
	# IO
	def io(self):
		"""
		Raises NotImplementedError. Subclasses must override this method
		to receive and handle messages as appropriate.
		"""
		raise NotImplementedError("io-not-implemented")
	
	
	# STOP
	def stop(self):
		"""
		Stop looping in the run() method; Sets self.running to False.
		
		NOTE: This has the effect of exiting a launched task; for tasks
		      or hubs in threads, it merely stops the run loop without
		      closing, leaving the object in memory and able to run() or
		      start() again.
		"""
		if self.running:
			self.__running = False
			self.__threaded = False
		self.log("STOP", "running=%s" % (str(self.running)))
	
	
	# CLOSE
	def close(self):
		"""
		Call onClose(), giving subclasses a chance to close any files,
		connections, etc... that may have been opened by a previous call
		to onOpen(). Sets active to False.
		
		NOTE: This method has no effect if the active property is already
		      set to False.
		"""
		if self.active:
			self.onClose()
			self.__active = False
			self.log("CLOSE")
	
	
	# EXIT
	def exit(self):
		"""
		Calls stop() and then close().
		"""
		try:
			self.stop()
		finally:
			self.close()
	
	
	
	#
	# CALLBACKS
	#
	
	# ON-OPEN
	def onOpen(self):
		"""
		Subclasses override to open any connections they need.
		"""
		pass
	
	
	# ON-CLOSE
	def onClose(self):
		"""
		Subclasses override to close any connections opened onOpen().
		"""
		pass
	
	
	# ON-MESSAGE
	def onMessage(self, m):
		"""
		Handles the 'exit' message by calling self.exit().
		"""
		if 'c' in m:
			if m['c'] == 'exit':
				m['r'] = 'exiting'
				self.put(m)
				self.exit()
				return
	
	
	# STATUS
	def status(self):
		"""
		Return a dict containing status information. This method sets
		active, running, and threaded to their corresponding values. A
		time key is also added with the current time.time().
		"""
		return dict(
			active = self.active,
			running = self.running,
			threaded = self.threaded,
			time = time.time()
		)
	
	
	# START
	def start(self):
		"""
		Calls the run() method in a new thread. This is convenient for
		running a hub process in an interactive application or script, or
		in the python interpreter.
		"""
		try:
			thread.start_new_thread(self.run, (None,))
			self.__threaded = True
			time.sleep(self.sleep)
			self.log("START")
		except Exception as ex:
			self.log(type(ex).__name__, ex.args)


