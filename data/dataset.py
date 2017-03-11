"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyro project, distributed under
the terms of the GNU Affero General Public License.

DATASET - Storage of loosely structured data.

Dataset manages a database that abstracts data storage into records,
fields, and values so as to reduce the space required to store data
on disk in cases where many field values are repeated.

The structure can be visualized like this:

  dataset      # each dataset has 0 or more records
	   |
  record       # each record has 1 or more fields
     |
   field       # each field has a tag and a data value
     |_ tag    # tag is like a feild name
     |_ data   # data is like the field's value

A dataset database has a table for each of these ideas (dataset, tag,
etc...). Any field containing an already-existing data item points to
that item, rather than creating a copy. This saves a lot of storage
space if many fields contain the same larger-than-an-int data value.
"""

from .. import *
#import time #included from ..


# import as 'thread' from python 2 or 3
try:
	import thread
except:
	import _thread as thread





#
# DATASETS
#
class Datasets (Base):
	"""
	The Datasets class represents a database that contains the tables
	that store data as needed by the Dataset class (defined below).
	"""
	
	def __init__(self, db=None, **k):
		"""
		The `db` argument must be a data.database.Database or a valid
		configuration specification for creating one. (See help for the
		Database constructor.)
		
		All args and kwargs will be applied to creating a database, but 
		only if the db argument is NOT a database.Database object. If the
		`db` argument is a Database object, kwargs are ignored.
		"""
		try:
			# First, assume db is a Database object; make sure it's open.
			if not db.active:
				db.open()
		except AttributeError:
			# If that raises an error, assume db is a config specification.
			k.setdefault('sql', DATASET_SQL)
			k['autoinit'] = True
			db = Base.ncreate('data.database.Database', db, **k)
			db.open()
		
		# private vars
		self.__db = db
			
	def __del__(self):
		self.__db.close()
		self.__db = None
	
	@property
	def db(self):
		return self.__db
	
	def dset(self, setname):
		"""
		Returns a Dataset object representing a named dataset from this
		`Datasets` database.
		"""
		# Pass the Database object and the name of the dataset stored
		# within that database.
		return Dataset(self.db, setname)





class Dataset (object):
	
	def __init__(self, db, setname):
		
		# set "db" first so the self.db calls below will work
		self.__db = db
		
		# store the set name; create the set if it doesn't 
		# already exist; get and store the set id.
		self.__setname = setname
		c = self.db.opq('set-find', (self.setname,))
		try:
			r = c.fetchone()
			self.__setid = r[0]
		except:
			self.db.opq('set-add', (self.setname,))
			c = self.db.opq('set-find', (self.setname,))
			r = c.fetchone()
			self.__setid = r[0]
			self.db.commit()
	
	
	
	@property
	def db(self):
		"""
		The data.database.Database object that contains the tables which
		store this dataset's data.
		"""
		return self.__db
	
	@property
	def setname(self):
		"""The name of this dataset, as stored in the database."""
		return self.__setname
	
	@property
	def setid(self):
		"""The set identifier, an integer."""
		return self.__setid
	
	# COUNT
	def count (self):
		"""Record count for this object's dataset."""
		c = self.db.opq("rec-ct", (self.setid,))
		return c.fetchone()[0]
	
	
	def search(self, tag, data, order='dt'):
		"""Return a cursor where tag matches data."""
		return self.db.opq("search-data", (self.setid, tag, data, order))
	
	
	def add(self, iterable=None, **k):
		"""
		Create new record
		Select new record's ID
		Loop through kwargs adding tag=data
		 - add/get tagid
		 - add/get dataid
		 - add field holding new recid/tagid
		
		NOTE: If tag already exists, the tagid
		      is returned. If the data already
		      exists, it's dataid is returned.
		
		NEW FEATURE:
		Since transactions are so slow, there's now an optional 
		`iterable` argument that, when given, loops adding all records
		before committing.
		"""
		# accept a list of dicts or just keyword args
		dicts = iterable or [k]
		
		for d in dicts:
			with thread.allocate_lock():
				self.db.opq('rec-add', (self.setid, time.time()))
				c = self.db.opq('rec-max', (self.setid,))
				recid=c.fetchone()[0]
				
				for kw in d:
					tagid = self.__tagAdd(kw)
					dataid = self.__dataAdd(d[kw])
					self.db.opq("field-add", (recid, tagid, dataid))
				
			self.db.commit()
	
	def __add(self, **k):
		with thread.allocate_lock():
			self.db.opq('rec-add', (self.setid, time.time()))
			c=self.db.opq('rec-max', (self.setid,))
			recid=c.fetchone()[0]
			
			for kw in k:
				tagid = self.__tagAdd(kw)
				dataid = self.__dataAdd(k[kw])
				self.db.opq("field-add", (recid, tagid, dataid))
		
	
	def __dataAdd(self, data):
		c = self.db.opq('data-find', (data,))
		x = c.fetchone()
		if x:
			return x[0]
		self.db.opq('data-add', (data,))
		return self.__dataAdd(data)
	
	
	def __tagAdd(self, tag):
		c = self.db.opq('tag-find', (tag,))
		x = c.fetchone()
		if x:
			return x[0]
		self.db.opq('tag-add', (tag,))
		self.db.commit()
		return self.__tagAdd(tag)




#
#	DATASET_SQL
#  - SQL for standard operations and to create the database
#
DATASET_SQL = {
		
		#
		# SQL TO CREATE DB TABLES/INDICES
		#
		"create" : [
			# dataset
			"""
			create table if not exists dataset (
				setid INTEGER, 
				setname TEXT, 
				PRIMARY KEY (setid)
			)
			""",
			"""
			create unique index if not exists ix_dataset 
				on dataset (setname)
			""",
			
			# record
			"""
			create table if not exists record (
				recid INTEGER,
				setid INTEGER,
				dt REAL,
				PRIMARY KEY (recid)
			)
			""",
			"""
			create index if not exists ix_record_dt 
				on record (dt)
			""",
			"""
			create index if not exists ix_record_set 
				on record (setid)
			""",
			
			# field
			"""
			create table if not exists field (
				recid INTEGER,
				tagid INTEGER,
				dataid INTEGER,
				PRIMARY KEY (recid, tagid, dataid)
			)
			""",
			"""
			create index if not exists ix_field_tag 
				on field (tagid)
			""",
			"""
			create index if not exists ix_field_data 
				on field (dataid)
			""",
			
			# tag
			"""
			create table if not exists tag (
				tagid INTEGER, 
				tag TEXT, 
				PRIMARY KEY(tagid)
			)""",
			"""
			create index if not exists ix_tag 
				on tag (tag)
			""",
			
			# data
			"""
			create table if not exists data (
				dataid INTEGER, 
				data TEXT, 
				PRIMARY KEY(dataid)
			)
			""",
			"""
			create index if not exists ix_data 
				on data (data)
			"""
		],
		
		#
		# SQL FOR DATASET OPERATIONS
		#
		"op": {
			"set-find": "select setid from dataset where setname=?",
			"set-add" : "insert into dataset (setname) values (?)",
			"set-list" : "select * from dataset order by ?",
			
			"rec-list" : "select * from record where setid=? order by ?",
			"rec-add" : "insert into record (setid, dt) values (?, ?)",
			"rec-max" : "select max(recid) from record where setid=?",
			"rec-ct" : """
				select count(recid) from record where setid=?
			""",
			
			"field-add" : """
				insert into field (recid, tagid, dataid) 
					values (?,?,?)
				""",
				
			"tag-find": "select tagid from tag where tag=?",
			"tag-add" : "insert into tag (tag) values (?)",
			"tag-list": "select * from tag order by ?",
			
			"data-find": "select dataid from data where data=?",
			"data-add" : "insert into data (data) values (?)",
			
			"search-data" : """
				select r.dt, s.setname, s.setid, r.recid, 
					t.tag, f.tagid, d.data, d.dataid
				from record r
					inner join dataset s on (s.setid = r.setid)
					inner join field f on (f.recid = r.recid)
					inner join data d on (f.dataid = d.dataid)
					inner join tag t on (f.tagid = t.tagid)
				where s.setid=? and t.tag=? and d.data like ?
				order by ?
			"""
		}
	}
