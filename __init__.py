"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyro project, distributed under the terms 
of the GNU Affero General Public License.

PYRO

This package is intended to provide support for python application
and script development and to be a helpful utility in an interpreter
or from the command line, and to work - at least to some degree - in
python version 2 and 3. It's the experimental playground for the pyro
project.

PYTHON 2/3 COMPATABILITY NOTES
The code here does a lot to help your scripts run in both python 2
and 3, but only if you `import *` from this module. Note that all
subpackages and modules import * from this module.

Here are some more 2/3 compatability tips:
 * Use the string class names as provided by python 2 - basestring, 
   unicode, and str. In python 3, they all are the same class, str,
   so they'll work as expected in either major version.
 * Use unichr even in 3 - it's defined (only in python 3) as chr, but
   this module defines unichr=chr for python 3 so that the code will
   work in python 2.

COMMAND LINE USE
Currently, there's not much available for use from the command line,
but there are several packages and modules under construction which
will be very useful from the command line.

Useful command line features:
 $ python -m pyro --clean

"""

import os, sys, time, traceback

try:
	basestring
except:
	basestring = unicode = str
	unichr = chr


# REM: Set to True for development, False for release versions.
AUTO_DEBUG = True


DEF_INDENT = 2
DEF_ENCODE = 'utf_8'



#
# BASE - A base for non-utility classes
#
class Base(object):
	
	@classmethod
	def config(cls, *a, **k):
		try:
			return cls.__TConfig(*a, **k)
		except:
			cls.__TConfig = TFactory(cls.innerpath('fs.config.Config')).type
			return cls.__TConfig(*a, **k)
	
	@classmethod
	def create(cls, conf, *a, **k):
		"""
		Uses a Factory to create an object as described by `conf` and 
		any additional args and kwargs. If conf is the path to an 
		existing file, then it will be converted to a configuration dict.
		Otherwise, it should be a type or the text representation of a 
		type in the form "package.module.class".
		
		See the Factory class help for details about argument specs.
		"""
		if isinstance(conf, basestring):
			# Don't allow Path.expand to raise an exception if the file
			# doesn't exist; in such a case, conf is a type description 
			# string.
			path = cls.path().expand(conf, affirm=None)
			if os.path.exists(path):
				conf = cls.config(path)
		
		# Create and return the object described by conf.
		return Factory(conf, *a, **k).create()
	
	@classmethod
	def innerpath(cls, innerPath=None):
		"""
		Return the full Factory type descriptor string given the path to
		an object from within the pyro module. Don't prefix the innerPath
		argument with "pyro." as that is automatically prepended by this
		classmethod when necessary).
		
		This feature is used within the pyro package when creating new
		objects from within the pyro package so that the correct type
		description string generated even when pyro is not a top-level
		package.
		"""
		#m = '.'.join(cls.__module__.split('.')[:-1])
		m = cls.__module__
		p = '.%s' % (innerPath) if innerPath else ''
		return "%s%s" % (m, p) if m else innerPath

	@classmethod
	def ncreate(cls, innerPath, *a, **k):
		"""
		Expand `innerPath` argument through Base.innerpath then create
		and return the described object.
		"""
		return cls.create(cls.innerpath(innerPath), *a, **k)
	
	@classmethod
	def path(cls, *a, **k):
		try:
			return cls.__TPath(*a, **k)
		except:
			cls.__TPath = TFactory(cls.innerpath('fs.Path')).type
			return cls.__TPath(*a, **k)





#
# T-FACTORY - Type Factory
#
class TFactory(object):
	
	# class values
	FACTORY_LEVEL = 0
	__cache = {}
	
	def __init__(self, typeInfo):
		"""
		Pass a string value representing the python path to an available
		type in the form: package[.package...].module.Type; Alternately,
		pass a dict containing a type key with a type description string
		value (in the same format).
		
		NOTE:
		The type is not actually loaded until requested by a call to the
		TFactory.type property. This may change in future releases if
		this delay appears to be causing debugging difficulties.
		"""
		self.__typeinfo = typeInfo
	
	@property
	def level(self):
		"""
		Return the 'level' value to be passed to __import__ when loading
		a module for creation of a type.
		"""
		try:
			return self.__level
		except:
			self.__level = TFactory.FACTORY_LEVEL
			return self.__level
	
	@level.setter
	def level(self, i):
		"""
		Set the 'level' value to be passed to __import__ when loading a
		module for creation of a type.
		"""
		self.__level = i
	
	@property
	def type(self):
		"""
		Returns the type specified by the typeInfo argument provided to
		this object's constructor.
		"""
		try:
			return self.__type
		except AttributeError:
			self.__type = self.__calctype()
			return self.__type
	
	#
	# CALC TYPE
	# - this was previously handled in Factory __init__
	#
	def __calctype(self):
		# if typeinfo is a dict, get 'type' key from dict
		if isinstance(self.__typeinfo, dict):
			self.__typeinfo = self.__typeinfo.get('type')
		
		# assume it's a string type definition...
		if isinstance(self.__typeinfo, basestring):
			return self.__ftype(self.__typeinfo)
			
		# I can't think of a single practical use for the following; I'll
		# comment it, for now, and wait to see whether it's missed.
		#elif type(self.__typeinfo) == type:
		#	return self.__typeinfo
		
		# otherwise, raise ValueError (rather than TypeError, since the
		# type is just the value we're expecting)
		else:
			raise ValueError('factory-type-invalid', xdata(
				reason="type-desc-invalid", type=str(self.__typeinfo)
			))
	
	#
	# F-TYPE - converts a string type-description to an actual type,
	#          then caches the type in the class.__cache dict
	#
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
			raise TypeError('factory-type-fail', xdata(
				type=sType, path=sFull
			))
		self.__cache[id] = T
		return T
	
	#
	# F-IMPORT - load a type given string path (package.module.Type)
	#
	def __fimport(self, path, T=None):
		try:
			return __import__(
				str(path), globals(), locals(), str(T), self.level
			)
		except Exception as ex:
			raise type(ex)('factory-import-fail', xdata(
				python=str(ex), path=path, T=T, 
				typeinfo=self.__typeinfo, suggest=[
					'check-file-path', 'check-class-path','check-python-syntax'
				]
			))





#
# FACTORY
#
class Factory(TFactory):
	"""A simple, generic factory class."""
	
	def __init__(self, conf, *args, **kwargs):
		"""
		Argument `conf` is a dict containing:
		  type   : string describing the object to create
		  args   : list of arguments for object's constructor
		  kwargs : a dict of keyword arguments for constructor
		
		If conf argument is *not* a dict, it will be taken as a type
		description. Additional optional args and kwargs will be passed
		directly to the new object (of type 'type') when its created.
		
		Type description strings should be in the form of a fully 
		qualified import description followed by the object type or class
		name. (Eg. "pyro.hubcap.Hub"). See TFactory's init help.
		"""
		TFactory.__init__(self, conf)
		
		# get type, args, and kwargs from config dict
		if isinstance(conf, dict):
			self.__a = args if args else conf.get('args', [])
			self.__k = kwargs if kwargs else conf.get('kwargs', {})
		else:
			self.__a = args
			self.__k = kwargs if kwargs else {}
	
	
	# CALL
	def __call__(self, *a, **k):
		"""Calls self.create() passing args/kwargs; returns result."""
		return self.create(*a, **k)
	
	
	# CREATE
	def create(self, *a, **k):
		"""
		Returns an object described by constructor arguments. If any args
		are passed to this method, they replace all args as stored by the
		constructor. Any given kwargs update a copy of the kwargs given 
		to the constructor.
		"""
		kk = dict(self.__k)
		kk.update(k)
		a = a if a else self.__a
		return self.type(*a, **kk)






def tracebk():
	"""Return current exception's traceback as a list."""
	tb = sys.exc_info()[2]
	if tb:
		try:
			return list(traceback.extract_tb(tb))
		finally:
			del(tb)



def xdata(xdata=None, **k):
	"""
	Package extensive exception data into a dict to be passed as the
	second argument to a new exception. This classmethod merges any
	given keyword args, exception type, args, and traceback values 
	with dict `xdata` into a new dict suitable for display by the 
	Debug class.
	
	The xdata argument is optional, defaulting to an empty dict. Any
	keywords (also optional) will update the xdata dict.
	
	Existing exceptions are chained in the current result's `prior` 
	key value, and multiple new exceptions are added as they are 
	processed by the xdata classmethod.
	
	NOTES:
	 * The pyro package standard is to pass a 'dash-separated-error'
	   string as the first argument and an xdata dict as the second 
	   argument in any exception thrown (or caught and rethrown)..
	"""
	# argument management
	xdata = xdata or {}
	xdata.update(k)
	
	# forced arguments
	xdata.setdefault('time', time.time())
	
	# create and populate the return dict
	r = dict(detail=xdata)
	
	# if this is a current exception situation, record its values 
	try:
		xtype, xval = sys.exc_info()[:2]
		xprior = {}
		if xtype or xval:
			xprior['xtype'] = xtype
			xprior['xargs'] = xval.args
			tblist = tracebk()
			if tblist:
				xprior['tracebk'] = list(tblist)
			r['prior'] = xprior
		return r
	finally:
		# Some versions of python may encounter problems if these values,
		# are not nullified.
		xtype = None
		xval = None




#
# DEV / DEBUG
#
def debug(debug=True, showtb=True):
	"""Enable/disable debugging/traceback."""
	TFactory(Base.innerpath('dev.debug')).type(debug,showtb)

if AUTO_DEBUG:
	debug()
