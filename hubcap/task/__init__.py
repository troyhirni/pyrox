"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyro project, distributed under the terms 
of the GNU Affero General Public License.

TASK

This package contains the somewhat abstract base Task class and a
demo task subclass.


"""

from ..runner import *




# ABSTRACT TASK (no run method)
class Task(Runner):
	
	def __init__(self, config={}, **k):
		"""
		When creating a Task-based object, the factory config dict must 
		specify as its first argument a dict containing any values 
		necessary for configuration of the Task subclass.
		
		Note that keyword arguments will overwrite like keys in the
		config dict, and that Hub-specified keyword arguments will always
		include qhub and qtask keys sepcifying multiprocessing queues for
		communication.
		"""
		conf = config or {}
		Runner.__init__(self, conf, **k)
		conf.update(k)
		self.qhub = conf['qhub']
		self.qtask = conf['qtask']
		self.log("task init ok")
	
	
	def get(self):
		try:
			return self.qtask.get(HC_Q_TIMEOUT)
		except:
			return None
	
	
	def put(self, m=None, **k):
		m = m or {}
		m.update(k)
		self.qhub.put(dict(m))
	
	
	def io(self):
		"""
		Read incomming messages and send them to self.onMessage()
		"""
		# use local variables to speed up the io loop
		g = self.get
		om = self.onMessage
		
		# read and process messages until the input queue is empty
		m = self.get()
		while m:
			om(m)   #self.onMessage()
			m = g() #self.get()
	
	
	def onMessage(self, m):
		"""
		The Task onMessage handler processes the 'exit' command, which 
		is passed in a message dict as {'c':'exit'}
		"""
		self.log("received message", m)
		if 'c' in m:
			if m['c'] == 'exit':
				self.log("received exit message", m)
				m['r'] = 'exiting'
				self.put(m)
				self.stop()
				self.log("returned-from-stop", running=self.running)
		else:
			m['e'] = 'unhandled-message'
			self.put(m)
		
		self.log("processed message", m)



