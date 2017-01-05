"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyro project, distributed under the terms 
of the GNU Affero General Public License.

HUB





"""

from .runner import *


class Hub(Runner):
	
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
	
	
	
	
	def __init__(self, config=None, **k):
		conf = config or {}
		Runner.__init__(self, conf)
		self.tasks = {}
	
	
	def __del__(self):
		try:
			self.exit()
		except Exception as ex:
			self.log(type(ex).__name__, ex.args)
	
	
	# messaging
	
	def get(self, taskid):
		trec = self.tasks[taskid]
		qhub = trec['qhub']
		try:
			return qhub.get(timeout=HC_Q_TIMEOUT)
		except:
			return None
	
	
	def put(self, taskid, m=None, **k):
		m = m or {}
		m.update(k)
		tr = self.tasks[taskid]
		tr['qtask'].put(m)
	
	
	# orisc
	
	def run(self, *a):
		"""
		Run this hub. 
		
		NOTES:
		 * At this point in development, control does not return from
		   the .run() method until it's time to exit, so call .exit()
		   to release all task processes.
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
	
	
	def io(self):
		"""
		Handle one pass through the event loop, reading and responding
		to any received messages from each task.
		"""
		for t in self.tasks.keys():
			if t in self.tasks: # ignore missing tasks
				m = self.get(t)
				while m:
					if 'a' in m:
						print json.dumps(m)
					elif 'c' in m:
						print
						print "FOO BANG!"
						print json.dumps(m)
						print
					
					m = self.get(t)
	
	
	# task control
	
	def taskexit(self, taskid):
		self.log("TASK-EXIT", taskid=taskid)
		if not taskid in self.tasks:
			self.log("TASK-NOT-FOUND", taskid=taskid)
			return
			
		self.put(taskid, {'c':'exit'})
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
	
	
	# hub exit
	
	def exit(self):
		if self.running:
			try:
				self.log("HUB-EXIT")
				tt = self.tasks.keys()
				for taskid in tt:
					self.taskexit(taskid)
				self.tasks = {}
			finally:
				self.stop()
	


+