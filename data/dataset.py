"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyro project, distributed under
the terms of the GNU Affero General Public License.

DATASET - Loosely structured database.

Dataset manages a database that abstracts data storage into records,
fields, and values so as to reduce the space required to store data
on disk in cases where many field values are repeated.

"""

from .. import *
#import time #included from ..


# import as 'thread' from python 2 or 3
try:
	import thread
except:
	import _thread as thread





#
# DATASET
#
class Dataset (Base):
	
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
		except Exception:
			# If that raises an error, assume db is a config specification.
			k.setdefault('sql', DATASET_SQL)
			db = ncreate('data.database.Database', db, **k)
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
		return DSet(self, setname)





class DSet (object):

	def __init__(self, ds, setname):
		
		# set "ds" first so the self.db calls below will work
		self.__ds = ds #util.proxify(ds)
		
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
	def ds(self):
		return self.__ds
		
	@property
	def db(self):
		return self.__ds.db
	
	@property
	def setname(self):
		return self.__setname
	
	@property
	def setid(self):
		return self.__setid
	
	# COUNT
	def count (self):
		"""
		Record count for this object's dataset.
		"""
		c = self.db.opq("rec-ct", (self.setid,))
		return c.fetchone()[0]
	
	
	def search(self, tag, data, order='dt'):
		"""
		Returns a cursor where tag matches data.
		"""
		return self.db.opq("search-data", (self.setid, tag, data, order))
	
	
	def add(self, **k):
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
		"""
		with thread.allocate_lock():
			self.db.opq('rec-add', (self.setid, time.time()))
			c=self.db.opq('rec-max', (self.setid,))
			recid=c.fetchone()[0]
			
			for kw in k:
				tagid = self.__tagAdd(kw)
				dataid = self.__dataAdd(k[kw])
				self.db.opq("field-add", (recid, tagid, dataid))
			
			self.db.commit()
	
	
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
