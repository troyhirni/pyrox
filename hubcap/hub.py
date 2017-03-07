"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyro project, distributed under the terms 
of the GNU Affero General Public License.

HUB





"""

from .runner import *


class Hub(Runner):
	"""
	The center of a hub-controlled app, Hub spawns Task processes that
	handle the work.
	
	Hub will eventually pass messages between tasks and handle utility
	needs such as authentication.
	"""
	
	# INIT
	def __init__(self, config=None, **k):
		conf = config or {}
		Runner.__init__(self, conf)
		self.tasks = {}
		self.auto = conf.get('autolaunch', [])
		self.factory = conf.get('factory', {})
		
		# debug formatting
		self.fout = Base.ncreate('fmt.JDisplay')
	
	
	def __del__(self):
		try:
			self.exit()
		except Exception as ex:
			self.log(type(ex).__name__, ex.args)
	
	
	
	#
	# ORISC
	#
	
	# OPEN
	def open(self, *a):
		"""
		Launch all preconfigured tasks.
		"""
		Runner.open(self)
		for k in self.auto:
			if k in self.factory:
				self.tasklaunch(k, self.factory[k])
			else:
				self.log('hub-missing-factory', key=k)
	
	
	# RUN
	def run(self, *a):
		"""
		Run this hub. 
		
		NOTES:
		 * At this point in development, control does not return from
		   the .run() method until it's time to exit; Use the start()
		   method when running from the python interpreter so you'll be
		   able to continue to send commands to the hub (and to tasks,
		   through the hub).
		 * When running this hub from a thread, the run() method is 
		   called by the Runner.start() method inside a new thread; this
		   is why control returns (eg, to the interpreter) immediately.
		"""
		try:
			# control stays with Runner.run until it's time to exit
			Runner.run(self, *a)
		finally:
			# ...so, exit (to close all running task processes
			self.exit()
			time.sleep(self.sleep)
	
	
	# IO
	def io(self):
		"""
		Handle one pass through the event loop, reading and responding
		to any received messages from each task.
		"""
		
		# loop using local variables
		om = self.onMessage
		get = self.get
		keys = self.tasks.keys()
		
		# loop through each task, processing messages
		for t in keys:
			
			# Ignore missing tasks - they'll be gone the next time through
			# the enclosing loop.
			if t in self.tasks:
				
				# limit the number of messages to be handled each loop
				imx = 32
				ict = 0
				
				# get and handle messages from this tasks output queueAl
				m = get(t)
				while m:
					om(m)
					ict += 1
					if ict >= imx:
						break
					m = get(t)
	
	
	# EXIT - STOP/CLOSE
	def exit(self):
		"""
		Exit all tasks then stop and close the hub.
		"""
		if self.running:
			try:
				self.log("HUB-EXIT")
				tt = self.tasks.keys()
				for taskid in tt:
					self.taskexit(taskid)
				self.tasks = {}
			finally:
				try:
					self.stop()
				finally:
					self.close()
	
	
	
	#
	# MESSAGING
	#
	
	def onMessage(self, m):
		"""
		This is where messages will be handled. For now, in early
		development, I'll just print them so I can see what's going on.
		"""
		# print out message in configured format (default: JDisplay)
		self.fout.output(m)
	
	
	
	# GET
	def get(self, taskid):
		"""
		Pop and return one item from the specified task's output queue. 
		Returns None if no message item exists in the queue.
		"""
		trec = self.tasks[taskid]
		qhub = trec['qhub']
		try:
			return qhub.get(timeout=HC_Q_TIMEOUT)
		except:
			return None
	
	
	# PUT
	def put(self, taskid, m=None, **k):
		"""
		Place item `m`, a dict, in the specified task's input queue.
		"""
		m = m or {}
		m.update(k)
		tr = self.tasks[taskid]
		tr['qtask'].put(m)
	
	
	
	#
	# TASK CONTROL
	#
	
	# TASK LAUNCH
	def tasklaunch(self, taskid, tasktype, *a, **k):
		"""
		The proper pre-configuration for a lists of hubcap Hub tasks is
		a dict in which each key is a taskid and each value a dict that
		contains `type`, `args`, and `kwargs` keys.
		
		Since tasks need not be based on the hubcap Task class, the 
		launch() function is designed to accept arguments in a sort of
		"freeform" way and the call to Process.run() will send them as
		specified in 
		"""
		
		# create communication queues
		qhub = multiprocessing.Queue()
		qtask = multiprocessing.Queue()
		
		# create a task record
		self.tasks[taskid] = dict(qhub=qhub, qtask=qtask)
		
		# force kwargs to carry THESE queues
		k.update(dict(qhub=qhub, qtask=qtask))

		# common argument to multiprocess.Process constructor
		n = "hubcap-%s" % (taskid)
		
		# prepare arguments
		aa = [tasktype]
		aa.extend(a)
		
		# Set up a Process object to run the task through the launch()
		# function with the given name, arguments, and kwargs.
		p = multiprocessing.Process(
			target=launch, name=n, args=aa, kwargs=k
		)
		
		# store the process object in the task record and start the task
		self.tasks[taskid]['p'] = p
		p.start()
		
		# now that task is running, update task record with process id
		self.tasks[taskid]['pid'] = p.pid
		
		# debug logging
		self.log("TASK-ADD", pid=p.pid, taskid=taskid,name=n)
		self.log("TASKS:", self.tasks.keys())
	
	
	# TASK EXIT
	def taskexit(self, taskid):
		self.log("TASK-EXIT", taskid=taskid)
		if not taskid in self.tasks:
			self.log("TASK-NOT-FOUND", taskid=taskid)
			return
			
		self.put(taskid, {'c':'exit'})
		
		while self.get(taskid):
			pass #ignore any remaining messages (?)
		
		time.sleep(self.sleep) #need an exit dict!
		
		self.log("WAIT-FOR-TASK-EXIT", taskid=taskid)
		for x in range(0,9):
			if not self.tasks[taskid]['p'].is_alive():
				break
			time.sleep(0.25)
		
		if self.tasks[taskid]['p'].is_alive():
			self.log('task %s failed to exit. terminating.' % taskid)
			self.tasks[taskid]['p'].terminate()
		
		del(self.tasks[taskid])
		self.log("TASKS:", self.tasks.keys())



