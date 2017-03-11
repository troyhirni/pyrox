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
		
		#print (conf)
		
		Task.__init__(self, conf)
		
		conf.setdefault('host', 'localhost')
		self.__host = conf['host']
		self.__port = conf['port']
		
		self.__server = None
	
	@property
	def host(self):
		return self.__host
	
	@property
	def port(self):
		return self.__port
	
	
	# STATUS
	def status(self):
		"""
		Add 'host' and 'port' to Task.status results...
		"""
		d = Task.status(self)
		d['host'] = self.__host
		d['port'] = self.__port
		return d
	
	
	# ON OPEN
	def onOpen(self):
		self.__server = Base.ncreate('net.sockwrap.SockWrap', 
				target=self, host=self.host, port=self.port
			)
		self.__server.listen()
	
	
	# ON CLOSE
	def onClose(self):
		self.__server.shutdown()
	
	
	# ON ACCEPT
	def on_accept(self, sa):
		# NOW What? -_-
		# let's see what we have...
		print ("ACCEPTED: %s" % str(sa))
		
	
	
	# Oops... Nope...
	"""
	# handle messages from hub
	def onMessage(self, m):
		if 'c' in m:
			if m['c'] == 'exit':
				self.send('server-exit')
				# Do not return! Allow superclasses to handle exit, too!
		
		# pass message on to the more basic handler
		Task.onMessage(self, m)
	
	
	# sockserv actions
	def send(
	"""
