"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under the terms 
of the GNU Affero General Public License.

HUBCAP - Hub-Controlled Apps

A central hub.Hub app creates, controls, and passes messages between
an arbitrary set of task.Task based apps running each in its own
process. This is an early demo/debugging/development version, but it
seems to work to some extent.
"""

from .. import *

import json, time, multiprocessing 
from multiprocessing import Queue


# Default sleep time when waiting for new tasks to collect in the
# input queue. Used by Runner.
HC_DEF_SLEEP = 0.1

# Timeout for queue.get() calls.
HC_Q_TIMEOUT = 0.001

#
# TEMPORARY! Debug log.
#
HC_DBG_LOG = '%s/hubcap.log' % (__path__[0])
HC_DBG_FMT = 'fmt.JDisplay'
HC_DBG_SHOW = True

def launch(typespec, *a, **k):
	"""
	Create an object based on the Task class and run it. Pass arguments
	as specified by base Factory class. 
	
	The Task and Hub classes must share two multiprocess queue objects:
	`qtask` receives messages from the hub, and `qhub` receives replies
	and messages from the task created here. The hubcap.Hub class must
	pass Process.run a set of arguments that, when passed to `create`  
	(and then to Factory.create), will get the correct set of arguments
	to the Task object's constructor.
	
	Here's an example dict that contains one task specification:
		'task1' : {
			'type' : 'pyro.hubcap.task.add1',
			'args' : [{'sleep':0.2}]
		}
	
	Here's a sort-of graphic showing the path the arguments follow:
		hub-config-dict -> Hub.taskLaunch() -> Process.run() -> launch() 
	
	The only way to accomodate both hubcap tasks and any other kind of
	task in general is to pass the all-important qhub and qtask as
	keyword arguments. No matter what you pass to Hub.tasklaunch as a
	keyword argument, the kwargs 'qhub' and 'qtask' are set to the 
	queue objects the Hub.tasklaunch() method creates.
	
	Therefore, custom task objects must be coded to accept keyword
	arguments to their constructor. All other arguments (and kwargs)
	will be received as specified in the factory configuration dict.
	"""
	# create and run the task
	t = Base.create(typespec, *a, **k)
	t.run()





class Hubcap(object):
	
	# create log formatter
	__LFMT = Base.ncreate(HC_DBG_FMT)
	
	# LOG
	def log(self, *a, **k):
		"""
		Write log messages to HC_DBG_LOG file in format HC_DBG_FMT.
		
		Pass any number of arguments and kwargs - the more debug info
		available, the better.
		"""
		if HC_DBG_LOG:
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
					
					# format log/debug string
					s = Hubcap.__LFMT.format(d)
					
					# log printing
					if HC_DBG_SHOW:
						print (s)
					
					# write to the log file
					f.write("%s: %s\n" % (str(time.time()), s))
				finally:
					f.close()
			except Exception as ex:
				print ("Logging Error!")
				print (ex)


