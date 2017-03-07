"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyro project, distributed under the terms 
of the GNU Affero General Public License.

SOCK-SERV - TCP Socket Server

            UNDER CONSTRUCTION
"""


from . import *



class SockServ(Task):
	
	# INIT
	def __init__(self, config=None, **k):
		conf = config or {}
		conf.update(k)
		Task.__init__(self, conf)
		
		self.__host = conf.get('host', 'localhost')
		self.__port = conf['port']
	
	@property
	def host(self):
		return self.__host
	
	@property
	def port(self):
		return self.__port
	
	def listen(self):
		pass # now what?


