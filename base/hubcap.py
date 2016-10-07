"""
HUBCAP - Hub-Centered Apps - UNDER CONSTRUCTION

With hubcap, one `Hub` processes runs at the center of a set of service
applications. The hub creates them, passes messages between them, and 
prints output to the terminal, interpreter, or a log file.

The hub process runs in the main thread of a process (or in a separete
thread if running from the python interpreter), controlling and passing
messages between task apps that run in separate processes.

Hubcap is part of the pyrox package.

NOTE:
 * Since the basic `Task` object is just the empty shell of a useful 
   program, the use of the word "Task" in this module's comments implies
   a subclass of the Task class that actually performs some meaningful
   purpose.


#
##  EXAMPLE 1 - Threaded Task (to be run in python interpreter)
#
import hubcap

# create a hub
h = hubcap.Hub()
h.start()

# create a task in a new thread
h.create('threadedTask')

# now the task must be started
d = h.get('threadedTask')

# write a command to the threaded task
h.writeto('threadedTask', dict(command='status'))


#
##  EXAMPLE 2 - Process Task (to be run in python interpreter)
#
import hubcap

# create a hub
h = hubcap.Hub()
h.start()

# create a task in a new process
h.launch('launchedTask')

# write a command to the launched task
h.writeto('launchedTask', dict(command='status'))

"""

#from pyrox.base import *
import json, multiprocessing, time
from multiprocessing import Process
from multiprocessing import Queue

try:
	import thread
except:
	import _thread as thread


DEF_SLEEP = 0.1
MIN_SLEEP = 0.000001
MAX_SLEEP = 10.0



# ----------------------------------------------------------------------
#
# HUBCAP
#
# ----------------------------------------------------------------------
class Hubcap(object):
	def error(self, *a):
		raise Exception(*a)




# ----------------------------------------------------------------------
#
# RUNNER
#
# ----------------------------------------------------------------------
class Runner (Hubcap):
	"""
	Base class for Hub and Task. This class is not fully implemented - it
	must be extended to define (at a minimum) the  handle(), read() and
	write() methods, which Hub and Task implement differently.
	
	NOTES:
	 * Implements basic process loop.
	 * Uses shared queues for messaging between hub and tasks.
	 * Call open() and run() to begin operation, then stop() and close()
	   to end operation - this is the correct order of operations.
	 * Subclasses override the onOpen() method to prepare for operation
	   and the onClose() method to tear down those preparations; The
	   handle() method is overridden to handle and reply to received
	   commands and/or messages;
	"""
	def __init__(self, config={}, **k):
		"""
		Base class for the central "hub" app and "task" apps running in
		separate processes.
		 * arg `config` must be a dict; kwargs replace config key values
		"""
		# kwargs override config key values
		config.update(k)
		
		# Config options
		self.__sleep = config.get('sleep', DEF_SLEEP)
		self.__slmin = config.get('sleep-min', MIN_SLEEP)
		self.__slmax = config.get('sleep-max', MAX_SLEEP)
		
		# sanitize sleep config
		if (self.__slmin > self.__slmax) or (self.__slmax < self.__slmin):
			self.error("invalid-sleep-range", "min-gt-max")
		elif self.__slmin < MIN_SLEEP:
			self.error("invalid-sleep-minimum")
		elif self.__slmax > MAX_SLEEP:
			self.error("invalid-sleep-maximum")
		elif (self.__sleep > self.__slmax) or (self.__sleep < self.__slmin):
			self.error("invalid-sleep-time")
		
		# runtime read-only
		self.__active = False
		self.__running = False
		self.__threaded = False
		self.__runtime = None
		self.__stoptime = None
	
	
	# DEL
	def __del__(self):
		"""
		Always shut down an object when it's deleted.
		"""
		self.shutdown()
	
	
	# RUNTIME READ-ONLY
	@property
	def active(self):
		"""True if this object has been opened, else False."""
		return self.__active
	
	@property
	def running(self):
		"""True if this object is running, else False."""
		return self.__running
	
	@property
	def threaded(self):
		"""True if this object is running in a thread, else False."""
		return self.__threaded
	
	@property
	def runtime(self):
		"""The unix time this object started running."""
		return self.__runtime
	
	@property
	def stoptime(self):
		"""The unix time this object stopped running."""
		return self.__stoptime
	
	
	# SLEEP (READ/WRITE)
	@property
	def sleep(self):
		"""
		Return or set the number of seconds (as a float) that this object 
		should sleep at the end of each pass through the run loop.
		
		When setting, quietly limits given sleep time argument to within 
		configured min/max range.
		"""
		return self.__sleep
	
	@sleep.setter
	def sleep(self, f):
		if f<self.__slmin:
			f = self.__slmin
		elif f>self.__slmax:
			f = self.__slmax
		self.__sleep = 0.0+f
	
	
	#
	# ORISC METHODS - Open, Run, IO, Stop, Close
	#
	
	# OPEN
	def open(self):
		"""Open this task, but don't begin running."""
		if self.__active:
			raise Exception('already-open')
		self.onOpen()
		self.__active = True
	
	def onOpen(self):
		"""
		Does nothing. Subclasses override to do whatever is necessary
		to initialize this object for "active" status.
		"""
		pass
	
	
	# RUN
	def run(self, *args):
		"""
		Start looping, calling the io() method repeatedly with a sleep
		after each loop.
		
		NOTE: Args are ignored! They only exist to fascilitate the use
		      of threads for testing/debugging/development. (See the
		      start() method.)
		"""
		if not self.__active:
			self.open()
		if self.__running:
			self.error("already-running")
		self.__running = True
		self.__runtime = time.time()
		try:
			while self.__running and self.__active:
				self.io()
		except Exception as ex:
			self.write({'message':"error", 'detail':ex})
		
		time.sleep(self.sleep)
	
	
	# IO
	def io(self):
		"""
		One pass through the event loop; handle received messages then
		sleep a little.
		"""
		# handle each queued task
		r = self.read()
		while r:
			self.handle(r)
			r = self.read()
		
		# sleep a while
		time.sleep(self.sleep)
	
	
	# STOP
	def stop(self):
		"""
		Stop running the event loop; exit thread if threaded.
		
		NOTE: The stop() method should NOT close() the object - if it's 
		      active, it should remain active.
		"""
		self.__running = False
		self.__threaded = False
		self.__stoptime = time.time()
	
	
	# CLOSE
	def close(self):
		"""
		Close this task, but don't stop running.
		
		NOTE: In practice, close() always comes after stop(); still, the 
		      distinction that close() does NOT call stop() can be important 
		      particularly when running in a thread rather than a separate
		      process (as in, when debugging from the python interpreter). 
		"""
		if self.__active:
			try:
				self.onClose()
			finally:
				self.__active = False
	
	
	def onClose(self):
		"""
		Does nothing. Subclasses override to do whatever is necessary
		to deactivate this object.
		
		NOTE: The close() method should NOT stop() the object; if it's 
		      running, it should remain running.
		"""
		pass
	
	
	
	#
	# UTILITY
	#
	
	# START (for debugging in the interpreter)
	def start(self):
		"""
		Start running in a thread. This is useful for testing/dev in the
		python interpreter (either Hub or Task), but is NOT intended for
		normal operation.
		"""
		self.__threaded = True
		thread.start_new_thread(self.run, (None,))
		time.sleep(self.sleep)
	
	# STATUS
	def status(self):
		"""
		Return a dict containing interesting status information.
		"""
		try:
			p = multiprocessing.current_process()
			pid = p.pid
		except:
			pid = None
		
		return {
			'active' : self.active,
			'running' : self.running,
			'threaded' : self.threaded,
			'runtime' : self.runtime,
			'stoptime' : self.stoptime,
			'pid' : pid if pid != None else "unknown"
		}
	
	# SHUTDOWN (convenience)
	def shutdown(self):
		"""
		Stop and close this object.
		
		NOTE: When testing in the python interpreter using a thread, this
		      object will stay in memory and can later be reopened and run
		      again. When running in a process, however, this will have 
		      the affect of exiting the process. In this case, a new Task
		      will need to be created using the Hub launch() method.
		"""
		try:
			self.stop()
		finally:
			self.close()





# ----------------------------------------------------------------------
#
# TASK
#
# ----------------------------------------------------------------------

class Task(Runner):
	"""
	TASK - A Task object is normally created and run in a separate 
	       process by the launch() function (as called by a Hub object)
	       but, being a Runner, it can be started for testing in the
	       python interpreter. 
	"""
	def __init__(self, config={}, **k):
		"""
		Pass config for Runner plus 'qhub' and 'qtask' keys, each containing
		an appropriate Queue. The 'qtask' key defaults to a new Queue object
		but the 'qhub' key is strictly required. Keyword args replace config
		key values.
		"""
		config.update(k) # kwargs override config key values
		Runner.__init__(self, config, **k)
		self.__qhub = config['qhub']
		self.__qtask = config['qtask']
	
	
	# HANDLE
	def handle(self, command):
		"""
		Default task simply returns the message "command-unhandled" to
		the Hub object.
		"""
		c = command.get('command', None)
		if c == 'exit':
			self.shutdown()
			self.write({
				'command' : command,
				'response' : 'exiting',
				'timestamp' : time.time()
			})
		
		elif c == 'status':
			self.write({
				'command' : command,
				'response' : self.status(),
				'timestamp' : time.time()
			})
		
		else:
			self.write({
				'command' : command,
				'response' : 'command-unhandled',
				'timestamp' : time.time()
			})
			
	
	# READ/WRITE
	def write(self, data):
		"""Write data to the hub."""
		self.__qhub.put(json.dumps(data))
	
	def read(self):
		"""
		Return any data sent from the hub, or None if no new data exists.
		"""
		if not self.__qtask.empty():
			return json.loads(self.__qtask.get())
		return None





# ----------------------------------------------------------------------
#
# HUB
#
# ----------------------------------------------------------------------

class Hub(Runner):
	
	def __init__(self, config={}, **k):
		"""
		A Hub can be created with little or no config since some (i hope)
		reasonable defaults are available for each key. Remember, though,
		that all the keys accepted by Runner can be set here as well.
		
		NOTE: While the Task class is pretty much useless without being
		      extended to perform some meaningful purpose, the Hub class is
		      (or should be and hopefully will be) complete in itself and
		      likely will never need to be extended.
		"""
		Runner.__init__(self, config, **k)
		self.__qhub = config.get('qhub', Queue())
		self.__tasks = {}
	
	
	def handle(self, command):
		print (command)
	
	
	# TASKS
	@property
	def tasks(self):
		"""
		Return a list of currently running Task objects.
		"""
		return self.__tasks.keys()
	
	
	# CREATE
	def create(self, taskid, config={}, **k):
		"""
		Creates a Task and adds it to the tasks list. Pass `taskid` (a dict
		key) and `config` (the config dict for creation of the task). Any 
		kwargs apply to the task config. The hub queue is provided by this
		method - if supplied, it will be ignored.
		
		NOTE: The `create` method is intended mainly for debugging. It
		      starts a new task in a thread within this hub's process.
		"""
		if taskid in self.__tasks:
			self.error('task-id-exists')
		
		# create the configuration
		config.update(k)
		config['qhub'] = self.__qhub
		config['qtask'] = Queue()
		
		# create the task record
		d = {
			'q' : config['qtask'],
			't' : Task(config, **k)
		}
		
		# store this task in the task list
		self.__tasks[taskid] = d
		
		# start the task
		d['t'].start()
	
	
	# LAUNCH
	def launch(self, taskid, config={}, **k):
		"""
		Launch a process to run() a Task. This is the best way to run a 
		task, since multiple processors can really speed up operation this
		way.
		"""
		if taskid in self.__tasks:
			self.error('task-id-exists')
		
		# create config
		config.update(k)
		config['qhub'] = self.__qhub
		config['qtask'] = Queue()
		
		# create the process object
		p = multiprocessing.Process(
				target=launchRunner, name="hubcap.%s" % taskid, args=(config,)
			)
		
		# create the task info dict
		d = {
			'q' : config['qtask'],
			'p' : p
		}
		
		# store this task in the task list
		self.__tasks[taskid] = d
		
		# start the task in it's own process
		d['p'].start()
	
	
	# GET
	def get(self, taskid):
		"""
		Returns a dict with information relevant to the task identified by
		the `taskid` argument. If no such task exists, an exception will be
		raised.
		
		The dict returned is guaranteed to have a 'q' key, containing the
		Queue object into which messages to the identified task can be sent.
		Typically, there's also a 'p' key, containing the Task's Process
		object. If the task is running in a thread, there will be a 't' key
		(instead of 'p') containing the actual Task object.
		
		MORE: Each Task object typically will run in it's own external 
		      process, but remember that tasks MAY be created to run in
		      their own individual threads within the Hub's process. The
		      returned dict will contain a 't' key (with the value being
		      the actual Task object) if the task is running in a thread 
		      within the Hub's process, or a 'p' key (value, the process
		      object) if the task is running in its own process.
		"""
		if not taskid in self.__tasks:
			self.error('task-not-found')
		return self.__tasks[taskid]
	
	
	# REMOVE
	def remove(self, taskid):
		"""
		Remove the task identified by taskid. If no such task can be found,
		an exception is raised. The process in which the task is running 
		should exit (though it sometimes hangs around 'defunct' for a while
		on some operating systems).
		
		NOTE: Removing a task that's running in the hub's thread may leave
		      task in memory (in the case where some variable still points
		      to the object). 
		"""
		if not taskid in self.__tasks:
			self.error('task-not-found')
		self.__tasks[taskid].write('exit') # NYI
		del(self.__tasks[taskid])
		
	
	#
	# READ/WRITE-TO
	#
	def writeto(self, taskid, data):
		"""
		Send (enqueue) a message to the Task object identified by `taskid`.
		The `data` argument should be a dict containing a 'command' key and
		any additional information required by the command as implemented by
		the task to which it's being sent.
		"""
		self.__tasks[taskid]['q'].put(json.dumps(data))
	
	def read(self):
		"""
		Returns the next item from the hub queue, or None if none exists.
		"""
		try:
			if not self.__qhub.empty():
				return json.loads(self.__qhub.get())
		except Exception as ex:
			pass
		return None


	# ON-CLOSE
	def onClose(self):
		"""
		When the Hub is closed, all tasks should be removed.
		"""
		for tid in self.__tasks:
			# get the task record from this Hub's task dict
			t = self.get(tid)
			
			# send the task
			t.write({'command': 'exit'})
		self.__tasks = {}





#
# FUNCTION: LAUNCH RUNNER
#
def launchRunner(config):
	"""
	Function in which a Task is launched.
	 - Runs in an external process.
	 - Used by Hub when opening (cleared when closing.)
	
	NOTE: This function should be called only by a Hub object. You can 
	      debug Task subclasses by running them in the interpreter. Use
	      task.start() to run a process in a separate thread and pass it
	      messages as the Hub would do.
	"""
	t = Task(config)
	try:
		t.open()
		t.run()
	finally:
		t.shutdown()


