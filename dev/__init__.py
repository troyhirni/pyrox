"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

DEV - Development-only tools

Debugging -	Call dev.debug() to turn on an exception that displays 
            exceptions in json display format (for readability).
            This is meant for use in a python interpreter.
"""


from ..fmt import *



def debug(debug=True, showtb=False):
	"""
	Controls a debug hook to show uncaught exceptions in a nice format. 
	Call debug(True) to start and debug(False) to go back to normal. If 
	second argument showtb is True, a traceback will be printed after
	debug data is displayed in the exception hook.
	"""
	Debug().debug(debug, showtb)



def debug_hook(t,v,tb):
	try:
		raise v
	except Exception as v:
		try:
			print (repr(type(v)))
			print (json.dumps( v.args, 
				sort_keys = True,
				indent    = DEF_INDENT, 
				cls       = JSONDisplay
			))
			if Debug.showtb():
				print ("Traceback:")
				traceback.print_tb(tb)
		
		except UnicodeDecodeError as uex:
			print ("Unicode Error")
			for x in uex.args:
				print (x)
			if Debug.showtb():
				print ("Traceback:")
				traceback.print_tb(tb)
		
		except BaseException as ex:
			print ("WARNING: DEBUG HOOK FAILED!")
			try:
				print (" - Exception type: %s" % (str(ex)))
			except:
				pass
			debug(False)


class Debug(object):
	__DEBUG = False
	__TRACE = False
	__SYSEX = sys.excepthook
	
	@classmethod
	def debug(cls, debug, showtb):
		cls.__DEBUG = True if debug else False
		cls.__TRACE = True if showtb else False
		if cls.__DEBUG:
			sys.excepthook = debug_hook
		else:
			sys.excepthook = cls.__SYSEX
	
	@classmethod
	def debugging(cls):
		return cls.__DEBUG
	
	@classmethod
	def showtb(cls):
		return cls.__TRACE




#
# INFORMATION
#

def dirpeek(obj):
	d = dir(obj)
	rd = {}
	for i,v in enumerate(d):
		rd[v] = getattr(obj,v)
	JDisplay(sort_keys=1).output(rd)

