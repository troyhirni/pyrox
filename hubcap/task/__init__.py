"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyro project, distributed under the terms 
of the GNU Affero General Public License.

TASK

This package defines the Task class, base for custom tasks that make
up a hub-controlled application.
"""

from ..runner import *



class Task(Runner):
	"""
	A Runner subclass that handles messaging for tasks.
	"""
	
	# INIT
	def __init__(self, config=None, **k):
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
		conf.update(k)
		Runner.__init__(self, conf)
		self.qhub = conf['qhub']
		self.qtask = conf['qtask']
		self.log("task init ok")
	
	# GET
	def get(self):
		"""
		Returns a message from the hub, or None if none exists.
		"""
		try:
			return self.qtask.get(HC_Q_TIMEOUT)
		except:
			return None
	
	
	# PUT
	def put(self, m=None, **k):
		"""
		Queues an outgoing message to the Hub.
		"""
		m = m or {}
		m.update(k)
		self.qhub.put(dict(m))
	
	
	# IO
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
			om(m)   # self.onMessage()
			m = g() # self.get()
	
	
	# CLOSE
	def close(self):
		"""
		Delete queues and close the Runner.
		"""
		del(self.qhub)
		del(self.qtask)
		Runner.close(self)
	
	
	# ON-MESSAGE
	def onMessage(self, m):
		"""
		The Task onMessage handler processes messages. All messages are
		dicts with key/value pairs that must be documented.
		
		This method handles the following commands:
		 - exit   : passed as dict(c='exit') # calls self.exit()
		 - status : passed as c='status'     # from self.status()
		 - debug  : passed as c='debug'      # raises an exception
		 
		Any message received that can't be handled is returned to the
		hub with key e='unhandled-message'
		"""
		if 'c' in m:
			if m['c'] == 'exit':
				m['r'] = 'exiting'
				self.put(m)
				self.exit()
			elif m['c'] == 'status':
				m['r'] = self.status()
			elif m['c'] == 'debug':
				raise Exception('debug-error', xdata(
					reason='triggered-by-user'
				))
		else:
			m['e'] = 'unhandled-message'
			self.put(m)
		
		self.log("processed message", m)



