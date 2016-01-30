"""
Copyright 2014-2016 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

BASE - Defintions needed by many modules in this package. Expect 
       many changes here during early experimental development. In
       the end, it will consist of most basic needs.
"""


import os, codecs, json



try:
	basestring
	textinput = raw_input

except:
	from imp import reload
	basestring = unicode = str
	unichr = chr
	textinput = input



DEF_INDENT = 2
DEF_ENCODE = 'utf_8'
FS_ENCODE = DEF_ENCODE




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
		MOD = self.__fimport(sPath, None, None, sType)
		T = MOD.__dict__.get(sType)
		if not T:
			raise TypeError('factory-type-fail', {
				'type':sType, 
				"path":sFull
			})
		self.__cache[id] = T
		return T
	
	
	# F-IMPORT
	def __fimport(self, Path, G=None, L=None, T=None):
		G = G if G else globals()
		L = L if L else locals()
		try:
			return __import__(str(Path), G, L, str(T), self.level)
		except Exception as ex:
			raise type(ex)('factory-import-fail', {
				'path' : Path,
				'python' : str(ex),
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
		open method if mode includes a 'b'. All kwargs are passed for 
		either option, so use only those that are appropriate to the 
		given mode.
		
		YOU MUST CLOSE!
		Returns the open file pointer. You'll need to close it when you
		are done with it.
		
		IMPORTANT: 
		 * To read binary data: theFile.read(mode="rb")
		 * To read unicode text: theFile.read(encoding="<encoding>")
		 * To write binary data: theFile.write(theBytes, mode="wb")
		 * To write unicode text: theFile.write(s, encoding="<encoding>")
		
		With mode "r" or "w", codecs automatically read/write the BOM
		where appropriate (assuming you specify the right encoding). 
		However, if you have text to save as encoded bytes, you can 
		do this so as to save BOM and bytes as encoded:
			>>> theFile.write(theBytes, mode="wb")
		
		This insures that byte string (already encoded) are written 
		"as-is", including the BOM if any, and can be read by:
			>>> s = theFile.read(encoding="<encoding>")
		"""
		if 'b' in mode:
			return open(self.path, **k)
		else:
			k.setdefault('encoding', FS_ENCODE)
			return codecs.open(self.path, mode, **k)
		
	# READER
	def reader(self, mode="r", **k):
		"""Open and read file at self.path."""
		return Reader(self.open(mode, **k))
	
	# WRITER
	def writer(self, mode="w", **k):
		"""Open and write data to file at self.path."""
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
			raise Exception('no-such-path', {'path' : path})
		if v and (not OP.exists(path)):
			if (v=='checkdir'):
				raise Exception('no-such-dir', {'path' : path})
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





class Config(object):
	
	def read(cls, filepath, mode="r", **k):
		"""Write config from the given file."""
		ss = Path(filepath).reader(mode, **k).read()
		try:
			try:
				return ast.literal_eval(ss)
			except:
				compile(ss, self.path, 'eval') #try to get a line number
				raise
		except:
			return json.loads(ss)
	
	def write(self, filepath, data, mode='w', **k):
		"""Write data to the given file as JSON."""
		jstring = json.dumps(data, indent=DEF_INDENT, cls=JSONDisplay)
		Path(filepath).writer(mode, **k).write(jstring)





