"""
Copyright 2014-2016 Troy Hirni
This file is part of the aimy project, distributed under
the terms of the GNU Affero General Public License.

Wrapper for databases that implement the DB-API 2.0 interface.
"""

try:
	from .. import base
except:
	import base

try:
	basestring
except:
	basestring = unicode = str


class Database(object):
	"""
	A wrapper for DB-API 2.0 database access. This class facilitates 
	cross-dbms, cross-python-version access to database functionality.
	"""
	
	def __init__(self, conf=None, **k):
		"""
		Pass a config dict with keys:
		 - module: a db-api module (eg, sqlite3)
		 - args  : arguments to be passed to the open() method
		 - sql   : a dict containing creation and operational sql
		 - path  : file path to the db file (if applicable).
		
		BE AWARE that path, if included, is prepended to args. 
		"""
		
		self.__con = None
		self.__mod = None
		self.__path = None
		self.__modname = None
		self.__inited = None
		
		#
		# Create from config...
		#
		if not conf:
			conf = {}
		elif isinstance(conf, basestring):
			conf = base.config(conf)
		
		# kwargs rule
		conf.update(k)
		
		# defaults
		conf.setdefault('module', 'sqlite3')
		
		# path, for file-based databases
		path = conf.get('path')
		self.__path = base.Path.expand(path) if path else None
		
		# arguments required to open the database.
		self.__args = conf.get('args', [])
		if self.__path:
			self.__args.insert(0, self.__path)
		
		# module
		m = conf.get('module')
		try:
			self.__mod = __import__(m)
			self.__modname = m
		except Exception as ei:
			try:
				self.__mod = m
				self.__modname = m.__name__
			except Exception as em:
				exdesc = {
					'err-import' : str(ei),
					'err-module' : str(em)
				}
				raise type(em)('db-init', exdesc)
		
		# sql
		self.__sql = conf.get('sql', {})
		if not isinstance(self.__sql, dict):
			raise TypeError('db-config-sql')
		self.__op = self.__sql.get('op', {})
		
		# init-check
		self.__autoinit = conf.get('autoinit')
	
	
	
	def __del__(self):
		self.close()
		
		
	@property
	def active (self):
		return True if self.__con else False
	
	@property
	def con (self):
		return self.__con
	
	@property
	def mod (self):
		return self.__mod
	
	@property
	def modname (self):
		return self.__modname
	
	@property
	def path (self):
		return self.__path
	
	@property
	def sql(self):
		return self.__sql
	
	@property
	def sop(self):
		return self.__op
	
	
	# CAT
	def cat(self, cat):
		"""
		Returns the named SQL query category as a list or a dict (as 
		defined in configuration).
		"""
		return self.__sql[cat]
		
	
	# CREATE
	def create(self):
		"""
		Initialize database using "create" category of the sql dict
		defined in config. This category is a list of sql statements
		intended to define tables and indices, and to populate tables
		if needed. Also creates a __corectl table with one field whose
		value is set to the current __corectl version, 2.
		"""
		cr = self.cat("create")
		if cr:
			self.qlist(cr)
		
		self.query("create table __meta (k,v)")
		self.query("insert into __meta values ('version', 3)")
		self.commit()
	
	
	
	# OPEN
	def open(self, **kwargs):
		"""
		Open database using preconfigured arguments and optional kwargs.
		"""
		if self.active:
			raise Exception('db-active')
		elif not self.mod:
			raise Exception('db-module')
		
		self.__con = self.mod.connect(*self.__args, **kwargs)
		
		# auto-init
		if not self.__autoinit:
			self.__inited = True
		elif not self.__inited:
			try:
				cc = self.query('select v from __meta where k="version"')
				self.__inited = True if cc.fetchone() else False
			except Exception as ex:
				self.create()
				cc = self.query('select v from __meta where k="version"')
				self.__inited = True if cc.fetchone() else False
				if not self.__inited:
					raise type(ex)('db-autoinit')
			finally:
				self.__autoinit = False
		
		return self
	
	
	# CLOSE
	def close(self):
		try:
			if self.__con and self.active:
				self.__con.close()
		finally:
			self.__con = None
	
	
	
	# EXEC
	def execute(self, *args):
		return self.__con.execute(*args)
	
	def executemany(self, *args):
		return self.__con.executemany(*args)
	
	def cursor(self):
		return self.__con.cursor()
	
	def commit(self):
		self.__con.commit()
	
	def rollback(self):
		self.__con.rollback()
	
	
	# ERROR ROLLBACK
	def __rollback(self):
		"""
		Used only in except clauses, in case the database was not open
		(or some other error not related to the sql itself). This keeps
		the wrong error from being raised.
		"""
		try:
			self.rollback()
		except:
			pass
	
	
	#
	# OPERATIONS
	#  - handle queries defined in the 'sql' config.
	#
	
	# QUERY
	def query(self, sql, *args):
		"""
		Execute query with given args; Rollback on error.
		"""
		try:
			return self.execute(sql, *args)
		except Exception as ex:
			if not self.active:
				raise Exception('db-inactive')
			self.__rollback()
			raise
	
	# Q-MANY
	def qmany(self, sql, *args):
		"""
		Just like query, but uses executemany.
		"""
		try:
			return self.executemany(sql, *args)
		except Exception:
			if not self.active:
				raise Exception('db-inactive')
			self.__rollback()
			raise
	
	# Q-LIST
	def qlist(self, queries, cursor=None):
		"""
		Execute list of query strings. On error, rollback.
		"""
		try:
			cc = cursor if cursor else self.cursor()
			for sql in queries:
				cc.execute(sql)
			return cc
		except Exception as ex:
			self.__rollback()
			raise
	
	
	# OPQ - Op Query
	def opq (self, qname, *args):
		"""
		Pass query name as defined in config in the 'op' section, and 
		any arguments required by the query; Executes the query and 
		returns a cursor.
		"""
		return self.query(self.__op[qname], *args)
	
	
	
	
