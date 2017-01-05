"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under the terms 
of the GNU Affero General Public License.

HUBCAP - Hub-Controlled Apps

A central hub.Hub app creates, controls, and passes messages between
an arbitrary set of task.Task based apps running each in its own
process. This is an early demo/debugging/development version, but it
seems to work to some extent.


cd dev
python

from pyrox.hubcap import hub
h = hub.Hub()
h.start()


h.tasklaunch(2, 'pyrox.hubcap.task.add1.Add1')
h.put(2, q=5)


h.put(2, c='exit')



"""

try:
	from ..base import *
	from .. import base
except:
	from base import *
	import base

import json, time, multiprocessing 


# Default sleep time when waiting for new tasks to collect in the
# input queue. Used by Runner.
HC_DEF_SLEEP = 0.1

# Timeout for queue.get() calls.
HC_Q_TIMEOUT = 0.001

#
# TEMPORARY! Debug log.
#
HC_DBG_LOG = '%s/hubcap.log' % (__path__[0])



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
	t = base.create(typespec, *a, **k)
	t.run()





class Hubcap(object):
	pass


