"""
Copyright 2014-2017 Troy Hirni
This file is part of the aimy project, distributed under
the terms of the GNU Affero General Public License.

Wraps database modules that implement the DB-API 2.0 interface.
"""


from .. import *



class Database(Base):
	"""
	A wrapper for DB-API 2.0 database access. This class facilitates 
	cross-dbms, cross-python-version access to database functionality.
	"""
	
	def __init__(self, config=None, *a, **k):
		"""
		Pass a config dict with keys:
		 - module: a db-api module or module name (default: "sqlite3")
		 - args  : arguments to be passed to the open() method.
		 - path  : file path to the db file (if applicable); if included,
		           this value is prepended to args.
		
		Or, pass the file path to the JSON or python text representation
		of a dict containing such a configuration.
		"""
		self.__con = None
		self.__inited = None
		
		# config
		conf = self.config(config, *a, **k)
		self.__path = conf.get('path')
		self.__args = conf.get('args')
		self.__mod = conf.get('module')
		self.__modname = conf.get('modname')
		self.__autoinit = conf.get('autoinit', False)
		
		# sql
		self.__sql = conf.get('sql', {})
		self.__op = self.__sql.get('op', {})
	
	
	def config(self, conf=None, *a, **k):
		"""Return a config dict based on the common pyro(x) rules."""
		try:
			return self.__config
		except:
			if not conf:
				conf = {}
			elif isinstance(conf, basestring):
				conf = Base.config(conf)
			else:
				conf = dict(conf)
			
			# kwargs rule
			conf.update(k)
			
			# defaults
			conf.setdefault('module', 'sqlite3')
			
			# Arguments required to open the database; As with kwargs, this 
			# also overrides any arguments specified in conf.
			conf['args'] = a if a else conf.get('args', [])
			
			# path, for file-based databases
			path = conf.get('path')
			if path:
				conf['path'] = Base.path().expand(path)
				conf['args'].insert(0, path)
			
			# module
			m = conf.get('module')
			try:
				conf['module'] = __import__(m)
				conf['modname'] = m
			except Exception as ei:
				try:
					conf['module'] = m
					conf['modname'] = m.__name__
				except Exception as em:
					exdesc = {
						'err-import' : str(ei),
						'err-module' : str(em)
					}
					exdesc['tracebk'] = Base.tracebk()
					raise Exception('db-init', exdesc)
			
			# sql
			conf['sql'] = conf.get('sql', {})
			if isinstance(conf['sql'], basestring):
				conf['sql'] = Base.config(conf['sql'])
			if not isinstance(conf['sql'], dict):
				raise TypeError('db-config-sql')
				
			# init-check
			conf['autoinit'] = conf.get('autoinit')
			
			self.__config = conf
			return conf
	
	
	
	def __del__(self):
		"""Close this database if open."""
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
		value is set to the current __corectl version, 3.
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
		
		try:
			self.__con = self.mod.connect(*self.__args, **kwargs)
		except BaseException as ex:
			raise type(ex)('db-open-fail', self.xdata())
		
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
					raise Exception('db-autoinit', self.xdata())
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
		"""Execute query with given args; Rollback on error."""
		try:
			return self.execute(sql, *args)
		except Exception as ex:
			if not self.active:
				raise Exception('db-inactive', self.xdata())
			self.__rollback()
			raise Exception('db-query-err', self.xdata(sql=sql))
	
	# Q-MANY
	def qmany(self, sql, *args):
		"""Just like query, but uses executemany."""
		try:
			return self.executemany(sql, *args)
		except Exception:
			if not self.active:
				raise Exception('db-inactive', self.xdata())
			self.__rollback()
			raise Exception('db-query-err', self.xdata(sql=sql))
	
	# Q-LIST
	def qlist(self, queries, cursor=None):
		"""Execute list of query strings. On error, rollback."""
		try:
			cc = cursor if cursor else self.cursor()
			for sql in queries:
				cc.execute(sql)
			return cc
		except Exception as ex:
			self.__rollback()
			raise Exception('db-query-err', self.xdata(sql=sql))
	
	
	# OPQ - Op Query
	def opq (self, qname, *args):
		"""
		Pass query name as defined in config in the 'op' section, and 
		any arguments required by the query; Executes the query and 
		returns a cursor.
		"""
		return self.query(self.__op[qname], *args)
	
	
	# OPS - Op Query List
	def ops (self, qname, *args):
		"""
		Execute a list of queries specified by an op name. This only 
		applies to op values that are lists of queries to execute.
		On error, rollback.
		"""
		try:
			xq = len(self.__op[qname])
			xa = len(args)
			xsql = self.__op[qname]
			for i in range(0, xq):
				sql = xsql[i]
				if (i<xa) and (args[i]):
					self.query(sql, args[i])
				else:
					self.query(sql)
		except:
			raise Exception(self.xdata())
	
	
	def xdata(self, **k):
		"""Return a dict containing debug information."""
		d = dict(module=self.__modname, active=self.active)
		if self.path:
			d['path'] = self.path
		return Base.xdata(d, **k)
