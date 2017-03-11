"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyro project, distributed under the terms 
of the GNU Affero General Public License.

INET - Internet Connectivity - Serve, Connect

Provides a Serve and Connect classes on which to base custom server 
connection classes. Serve does nothing on its own, but can be extended
to easily provide socket-based responses. Connect, as-is, is a socket
connection class that may be used to connect to any TCP server.
"""

import sockwrap



class WrappedSocket(object):
	def __init__(self, wrappedSocket):
		self.__sockserv = wrappedSocket
	
	def __del__(self):
		try:
			self.__sockserv.shutdown()
			del(self.__sockserv)
		except:
			pass
		finally
			self.__sockserv = None
	
	@property
	def timeout(self):
		"""Get set timeout."""
		self.__sockserv.timeout
	
	@timeout.setter
	def timeout(self, timeout):
		self.__sockserv.timeout = timeout
	
	@property
	def ctimeout(self):
		"""Get/Set connection timeout."""
		self.__sockserv.ctimeout
	
	@ctimeout.setter
	def ctimeout(self, connectionTimeout):
		self.__sockserv.ctimeout = connectionTimeout
	
	@property
	def bufsize(self):
		"""Get/Set buffer size."""
		self.__sockserv.bufsize
	
	@bufsize.setter
	def bufsize(self, bufsize):
		self.__sockserv.bufsize = bufsize
	
	@property
	def backlog(self):
		"""Server backlog value."""
		self.__sockserv.backlog
	
	@property
	def name(self):
		"""
		The address of the lockal socket, or None if not connected.
		"""
		return self.__sockserv.name
	
	@property
	def family(self):
		"""socket.family"""
		return self.__sockserv.family 
	
	@property
	def proto(self):
		"""socket.proto"""
		return self.__sockserv.proto
	
	@property
	def type(self):
		"""socket.type"""
		return self.__sockserv.type




class SocketServer(WrappedSocket):
	def __init__(self, config=None, **k):
		
		# read config, create socket
		conf = config or {}
		conf.update(k)
		
		# create socket
		self.__sockserv = sockwrap.SockWrap(conf, target=self)
		Wrapped.__init__(self, self.__sockserv)
		
		# always listening...
		self.__sockserv.listen()
	
	@property
	def listening(self):
		"""
		True if listening, else False
		"""
		return True if self.__pysock and self.__listening else False

	# ON-ACCEPT
	def on_accept(self, sa):
		return Handler(sa)





class SocketConnection(WrappedSocket):
	def __init__(self, config=None, **k):
		
		# read config, create socket
		conf = config or {}
		conf.update(k)
		
		# create socket
		self.__sockserv = sockwrap.SockWrap(conf)
		Wrapped.__init__(self, self.__sockserv)
		
		# always connected
		self.__sockserv.connect()
	
	
	@property
	def connected(self):
		"""
		True if connected, else False
		"""
		return True if self.__pysock and self.__connected else False
	
	@property
	def peer(self):
		"""
		The address of the remote connection, or None
		if not connected.
		"""
		return self.__pysock.getpeername() if self.connected else None
	
	# SEND
	def send(self, data, **k):
		if 'encoding' in k:
			data = data.encode(**Base.kcopy(k, 'encoding errors'))
		self.__sockserv.send(data)
	
	# RECV
	def recv(self):
		d = self.__sockserv.recv()
		if not d:
			return None
		if not ('encoding' in k):
			return self.__sockserv.recv()
		return d.decode(**Base.kcopy(k, 'encoding errors'))





class SocketHandler(WrappedSocket):
	def __init__(self, sa):
		
		# read config, create socket
		conf = config or {}
		conf.update(k)
		
		# create socket
		self.__sockserv = sockwrap.SockWrap(sock=sa[0], target=self)
		Wrapped.__init__(self, self.__sockserv)
	
	# SEND
	def send(self, data):
		self.__sockserv.send(data)
	
	# ON-RECV
	def on_recv(self, data):
		


