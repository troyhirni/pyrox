"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyro project, distributed under the terms
of the GNU Affero General Public License.

RUNNER - Abstract event loop implementation and support.

Runner is sort-of abstract. It's responsible for repeated calls to
an .io() method, which reads incomming messages and passes them to
an .onMessage() method.
"""


from .. import hubcap
from ..hubcap import *

try:
	import thread
except:
	import _thread as thread



class Runner(Hubcap):
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
		self.log("INIT")
	
	@property
	def sleep(self):
		return self.__sleep
	
	@property
	def active(self):
		return self.__active
	
	@property
	def running(self):
		return self.__running
	
	@property
	def threaded(self):
		return self.__threaded
	
	def open(self):
		self.log("OPENING")
		if self.active:
			raise Exception('open-fail',dict(reason='already-open'))
		self.onOpen()
		self.__active=True
		self.log("OPENED")
	
	def run(self, *a):
		"""
		Loop, processing incomming messages.
		"""
		if self.running:
			raise Exception("run-fail", dict(reason='already-running'))
		
		self.log("RUN")
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
		
		self.log("RUN-LOOP-ENDED")
		return 0
	
	
	def io(self):
		raise NotImplementedError("io-not-implemented")
	
	
	def stop(self):
		self.log("Runner.stop.entry")
		if self.running:
			self.log("STOPPING")
			self.__running = False
			self.log("RUNNING=%s" % (self.running?"True":"False")
		self.log("Runner.stop.exit")
	
	def close(self):
		if self.active:
			self.log("CLOSING")
			self.onClose()
			self.active = False
			self.log("CLOSED")
	
	
	# callbacks - these do nothing
	def onOpen(self):
		pass
	
	def onClose(self):
		pass
	
	def onMessage(self, m):
		if 'c' in m:
			if m['c'] == 'exit':
				self.log("received exit message", m)
				m['r'] = 'exiting'
				self.put(m)
				self.stop()
	
	
	# util
	def log(self, *a, **k):
		try:
			a = list(a)
			if k:
				a.append(k)
			f = open(HC_DBG_LOG, "a")
			try:
				p = multiprocessing.current_process()
				pid = p.pid
				T = type(self).__name__
				d = {
					'args' : a,
					'proc' : p._name,
					'pid' : pid,
					'type' : T
				}
				print (d)
				f.write("%s: %s\n" % (str(time.time()), json.dumps(d, indent=2)))
			finally:
				f.close()
		except Exception as ex:
			print ("Logging Error!")
			print (ex)
	
	def start(self):
		try:
			self.log("START")
			thread.start_new_thread(self.run, (None,))
			self.__threaded = True
			time.sleep(self.sleep)
			self.log("STARTED")
		except Exception as ex:
			self.log(type(ex).__name__, ex.args)


