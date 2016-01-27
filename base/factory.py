"""
Copyright 2014-2016 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

Factory
"""

try:
	from .. import base
except:
	import base

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
	def __fimport(self, Path, G=None, L=None, T=None, LV=None):
		G = G if G else globals()
		L = L if L else locals()
		LV = self.level if LV==None else LV
		try:
			return __import__(str(Path), G, L, str(T), LV)
		except Exception as ex:
			raise type(ex)('factory-import-fail', {
				'path' : Path,
				'python' : str(ex),
				'suggest' : ['check-file-path', 'check-class-path',
					'check-python-syntax']
			})

