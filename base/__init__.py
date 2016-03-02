"""
Copyright 2014-2016 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

BASE
 - Type defintions for reloading and for unicode in python 2 or 3
 - Basic config, factory, debug, unicode, and utility functionality
   and the constant variable definition to support it.
"""

import ast, codecs, json, os, sys, traceback, weakref


try:
	basestring
except:
	from imp import reload
	basestring = unicode = str
	unichr = chr


DEF_INDENT = 2
DEF_ENCODE = 'utf_8'



#
# CONFIG
#
def config(path, data=None, **k):
	"""
	Convenience function for reading/writing config files. If data is
	specified, it's written to the file at filepath. Otherwise, the 
	data at filepath is read and returned as an object.
	"""
	if data:
		Config(path).write(data, **k)
	else:
		return Config(path).read(**k)



#
# CREATE
#
def create(conf, *args, **kwargs):
	"""
	Uses a Factory to create an object as described by config and any 
	additional args and kwargs. If conf is the path to an existing 
	file, then it will be converted to a configuration dict. Otherwise, 
	it should be a type or the text representation of a type in the 
	form "package.module.class".
	"""
	if isinstance(conf, basestring):
		# Don't allow Path.expand to raise an exception if the file does
		# not exist; in such a case, conf is a type description string.
		path = Path.expand(conf, affirm=None)
		if os.path.exists(path):
			conf = config(path)
	
	# Create and return the object described by conf.
	return Factory(conf, *args, **kwargs).create()



#
# TYPE-RELATED UTILS
#
def typestr(x):
	"""
	Returns string in format 'module.class' for given type or object.
	"""
	if not isinstance(x, type):
		x = type(x)
	n = x.__name__
	m = x.__dict__.get('__module__')
	return '%s.%s'%(m,n) if m else n

def isproxy(x):
	"""True if x is a proxy, else False."""
	T = type(x)
	return issubclass(T, (weakref.ProxyType, weakref.CallableProxyType))

def proxify(o):
	"""Return o if it's a proxy, else proxy to o."""
	return o if (o==None) or isproxy(o) else weakref.proxy(o)



#
# DEBUGGING
#
def xdata(rdata={}, **k):
	"""
	Merge any given keyword args, exception type, args, and traceback 
	values with dict rdata into a new dict suitable for display
	by the Debug class. Return this new dict.
	"""
	rdata = dict(rdata)
	rdata.update(k)
	
	r = dict(detail=rdata)
	try:
		xtype, xval = sys.exc_info()[:2]
		if xtype:
			r['type'] = xtype
		if xval:
			r['args'] = xval.args
		tblist = tracebk()
		if tblist:
			r['tracebk'] = tblist
		return r
	finally:
		xtype = None
		xval = None


def tracebk():
	"""Return current exception's traceback as a list."""
	tb = sys.exc_info()[2]
	try:
		if tb:
			return traceback.format_tb(tb)
	finally:
		del(tb)


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
	except BaseException as v:
		try:
			print (repr(type(v)))
			print (json.dumps(
				v.args, cls=JSONDisplay, indent=DEF_INDENT, sort_keys=True
			))
			if Debug.showtb():
				print ("Traceback:")
				traceback.print_tb(tb)
		except:
			print ("WARNING: DEBUG HOOK FAILED!")
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
# FACTORY
#
class Factory(object):
	
	FACTORY_LEVEL = 0
	__cache = {}
	
	def __init__(self, conf, *args, **kwargs):
		# get type, args, and kwargs from config dict
		if isinstance(conf, dict):
			T = conf.get('type')
			A = args if args else conf.get('args', [])
			K = kwargs if kwargs else conf.get('kwargs', {})
		
		# in case conf is a type or type string
		else:
			T = conf
			A = args
			K = kwargs if kwargs else {}
		
		# Store Values as private variables
		self.__level = Factory.FACTORY_LEVEL
		self.__args = A
		self.__kwargs = K
	
		# get type (whether string or type)
		if isinstance(T, basestring):
			self.__type = self.__ftype(T)
		elif type(T) == type:
			self.__type = T
		else:
			tstr = "%s %s" %(str(type(T)), T)
			raise Exception('factory-type-invalid', {
				'conf' : conf,
				'type' : tstr,
				'args' : A,
				'kwargs' : K
			})
	
	def __call__(self, *a, **k):
		return self.create(*a, **k)
	
	@property
	def type(self):
		return self.__type
	
	@property
	def level(self):
		return self.__level
	
	@level.setter
	def level(self, i):
		self.__level = i
	
	
	# CREATE
	def create(self, *args, **kwargs):
		A = args if args else self.__args
		K = kwargs if kwargs else self.__kwargs
		if K:
			return self.__type(*A, **K)
		else:
			return self.__type(*A)
	
	
	# F-TYPE
	def __ftype(self, id):
		
		if id in self.__cache:
			return self.__cache[id]
		
		arPath = id.split('.')
		sFull = '.'.join(arPath)
		sType = arPath.pop()
		sPath = '.'.join(arPath)
		
		# try to handle system-defined types as well
		if sType in globals()['__builtins__'].keys():
			tt = globals()['__builtins__'][sType]
			if isinstance(tt, type):
				return tt
		
		# load from module
		MOD = self.__fimport(sPath, sType)
		T = MOD.__dict__.get(sType)
		if not T:
			raise TypeError('factory-type-fail', {
				'type':sType, 
				"path":sFull
			})
		self.__cache[id] = T
		return T
	
	
	# F-IMPORT
	def __fimport(self, Path, T=None):
		G = globals()
		L = locals()
		try:
			return __import__(str(Path), G, L, str(T), self.level)
		except Exception as ex:
			raise type(ex)('factory-import-fail', {
				'path' : Path,
				'python' : str(ex),
				'tracebk': tracebk(),
				'suggest' : ['check-file-path', 'check-class-path',
					'check-python-syntax']
			})





#
# PATH
#  - Base for fs module's classes.
#
class Path(object):
	"""Represents file system paths."""
	
	def __init__(self, p=None, **k):
		self.__p = self.expand(k.get('path', p), **k)
	
	def __str__(self):
		return self.path
	
	def __unicode__(self):
		return self.path
	
	@property
	def parent(self):
		return os.path.dirname(self.path)
	
	@property
	def path(self):
		return self.getpath()
	
	@path.setter
	def path(self, path):
		self.setpath(path)
	
	def exists(self, path=None):
		p = self.merge(path)
		return os.path.exists(p)
	
	def getpath(self):
		return self.__p
	
	def setpath(self, path):
		self.__p = path
	
	def isfile(self, path=None):
		return os.path.isfile(self.merge(path))
	
	def isdir(self, path=None):
		return os.path.isdir(self.merge(path))
	
	def islink(self, path=None):
		"""True if path is a symbolic link."""
		return os.path.islink(self.merge(path))
	
	def ismount(self, path=None):
		"""True if path is a mount point."""
		return os.path.ismount(self.merge(path))
	
	def touch(self, path=None, times=None):
		"""Touch file at path. Arg times applies to os.utime()."""
		p = self.merge(path)
		with open(p, 'a'):
			os.utime(p, times)  
	
	def merge(self, path):
		"""Returns the given path relative to self.path."""
		if not path:
			return self.path
		p = os.path.expanduser(path)
		if os.path.isabs(p):
			return os.path.normpath(p)
		else:
			p = os.path.join(self.path, p)
			return os.path.abspath(os.path.normpath(p))
	
	# OPEN
	def open(self, mode='r', **k):
		"""
		Open file at self.path with codecs.open(), or with the built-in
		open function if mode includes a 'b'. All kwargs are passed for 
		either option, so use only those that are appropriate to the 
		given mode.
		
		IMPORTANT:
		 * Returns an open file pointer; Close it when you're done. 
		 * To read binary data: theFile.read(mode="rb")
		 * To read unicode text: theFile.read(encoding="<encoding>")
		 * To write binary data: theFile.write(theBytes, mode="wb")
		 * To write unicode text: theFile.write(s, encoding="<encoding>")
		
		With mode "r" or "w", codecs automatically read/write the BOM
		where appropriate (assuming you specify the right encoding). 
		However, if you have text to save as encoded bytes, you can 
		do the following so as to save BOM and bytes as encoded:
			>>> theFile.write(theBytes, mode="wb")
		
		This insures that byte string (already encoded) are written 
		"as-is", including the BOM if any, and can be read by:
			>>> s = theFile.read(encoding="<encoding>")
		"""
		if 'b' in mode:
			return open(self.path, **k)
		else:
			k.setdefault('encoding', DEF_ENCODE)
			return codecs.open(self.path, mode, **k)
		
	# READER
	def reader(self, mode="r", **k):
		"""Open file at self.path and return a Reader."""
		return Reader(self.open(mode, **k))
	
	# WRITER
	def writer(self, mode="w", **k):
		"""Open file at self.path and return a Writer."""
		return Writer(self.open(mode, **k))
	
	@classmethod
	def expand(cls, path=None, **k):
		"""
		Returns an absolute path.
		
		Keyword 'affirm' lets you assign (or restrict) actions to be
		taken if the given path does not exist. 
		 * checkpath - default; raise if parent path does not exist.
		 * checkdir - raise if full given path does not exist.
		 * makepath - create parent path as directory if none exists.
		 * makedirs - create full path as directory if none exists.
		 * touch - create a file at the given path if none exists.
		
		To ignore all validation, pass affirm=None.
		"""
		OP = os.path
		if path in [None, '.']:
			path = os.getcwd()
		
		if not OP.isabs(path): # absolute
			path = OP.expanduser(path)
			if OP.exists(OP.dirname(path)): # cwd
				path = OP.abspath(path)
			else:
				path = OP.abspath(OP.normpath(path))
		
		v = k.get('affirm', "checkpath")
		if (v=='checkpath') and (not OP.exists(OP.dirname(path))):
			raise Exception('no-such-path', {'path' : OP.dirname(path)})
		if v:
			if OP.exists(path):
				if (v=='checkdir') and (not OP.isdir(path)):
					raise Exception('not-a-directory', {'path' : path})
			else:
				if (v=='checkdir'):
					raise Exception('no-such-directory', {'path' : path})
				elif v in ['makepath', 'touch']:
					if not OP.exists(OP.dirname(path)):
						os.makedirs(OP.dirname(path))
					if v == 'touch':
						with open(path, 'a'):
							os.utime(path, None)
				elif (v=='makedirs'):
					os.makedirs(path)
		
		return path





class Stream(object):
	def __init__(self, stream):
		self.__stream = stream
	
	def __del__(self):
		try:
			self.close()
		finally:
			self.__stream = None
	
	@property
	def stream(self):
		return self.__stream
	
	def close(self):
		self.__stream.close()





class Reader(Stream):
	def read(self, *a):
		return self.stream.read(*a)





class Writer(Stream):
	def write(self, data):
		return self.stream.write(data)





class Config(Path):
	
	def __init__(self, path, **k):
		Path.__init__(self, path)
		self.__k = k
	
	
	def write(self, data):
		"""Write data to this object's file path as JSON."""
		jstring = json.dumps(data, indent=DEF_INDENT, cls=JSONDisplay)
		self.writer("w").write(jstring)
	
	
	def read(self):
		"""Write config from this object's file path."""
		txt = self.reader("r", **self.__k).read()
		try:
			try:
				return ast.literal_eval(txt)
			except:
				compile(txt, self.path, 'eval') #try to get a line number
				raise
		except BaseException as ast_ex:
			try:
				return json.loads(txt)
			except BaseException as json_ex:
				# since this is reporting two exceptions, it can't use the
				# base.xdata function to package the exception data.
				raise Exception ("config-read-error", {
						"ast" : {
							"type" : type(ast_ex),
							"args" : ast_ex.args
						},
						"json" : {
							"type" : type(json_ex),
							"args" : json_ex.args
						},
						"tracebk" : tracebk()
					})





#
# JSON JSONEncoder
#  - Used by fs for writing config and by fmt for displaying JSON.
#
class JSONDisplay(json.JSONEncoder):
	"""
	Handles unparsable types by returning their representation to be
	stored as a string.
	"""
	def default(self, obj):
		try:
			return json.JSONEncoder.default(self, obj)
		except TypeError:
			return repr(obj)








