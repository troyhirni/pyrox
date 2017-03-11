"""
Copyright 2014-2015 Troy Hirni
This file is part of the aimy project, distributed under
the terms of the GNU Affero General Public License.

SOCK-WRAP - Wrapper for network connection sockets.

Use sockcon for client connections, sockserv for servers.
"""

from .. import *
import socket, select, struct



# GLOBALS (DEFAULTS)
SOCKWRAP_BUFSIZE = 4096
SOCKWRAP_TIMEOUT = 0.0001
SOCKWRAP_CTIMEOUT = 20



#
# SOCK VAL
# - Get values from python's socket module.
#
def sockval(val, default=None):
	"""
	Converts a string value for 'family', 'type', and
	'proto' to the value defined in the python socket 
	module. (May work for other values - test on each
	case to verify correct results are returned.)
	
	NOTE: Do NOT prefix string with 'socket.'
	
	DEFAULT ONLY USED IF VAL IS NONE
	Returns default if val is None (typically because
	it's not set in config). Otherwise, val is returned,
	even if it's False, 0, or ''.
	
	DEMO:
	net.sockval('AF_INET', 9) # returns socket.AF_INET
	net.sockval(False, 9) # returns False
	net.sockval('foofoo', 9) # returns 'foofoo'	
	net.sockval(None, 9) # returns 9
	"""
	try:
		if val in socket.__dict__:
			val = socket.__dict__[val]
	except Exception:
		pass
	return val if val != None else default





#
# SOCKET WRAPPER
#
class SockWrap(object):
	"""
	Wraps a standard python socket and manages
	connection or server activities.
	"""
	
	#
	# INIT
	#
	def __init__(self, config=None, **k):
		"""
		The config argument may be:
		 * A config dict.
		
		Config dict keys:
		 
		 REQUIRED, Either host/port:
		 * host    = ip address or host domain name as string
		 * port    = port as integer
		 
		 OR a connected socket object:
		 * sock    = a connected socket.socket object.
		 
		 OPTIONAL
		 * bufsize = read buffer size. default 4096
		 * timeout = read timeout. default 0.0001 sec.
		 * ctimeout = connect timeout. default 20 sec.
		
		IF CONNECTION TIMES OUT:
		Specify a longer ctimeout config value.
		
		SPECIFY ONLY A CONNECTED SOCKET (OR NONE):
		If you pass an unconnect socket to this 
		method its value will be quietly set to None.
		Passing an unconnected socked.socket object
		in the config's 'sock' key is like not giving
		anything at all there.
		
		I don't know how to tell if a socket's bound,
		so you can't pass a listening socket to SockWrap.
		"""
		c = config or {}
		c.update(**k)
		
		# host and port are required
		self.__host = c['host']
		self.__port = c['port']
		
		# runtime variables
		self.__target = c.get('target')
		self.__connected = False
		self.__listening = False
		
		# general config
		self.__bufsz = c.get('bufsize', SOCKWRAP_BUFSIZE)
		self.__tmout = c.get('timeout', SOCKWRAP_TIMEOUT)
		self.__ctmout = c.get('ctimeout', SOCKWRAP_CTIMEOUT)
		self.__bklog = c.get('backlog', socket.SOMAXCONN)
		
		# FOR SOCKET CREATION
		# - if connected socket is specified...
		self.__pysock = c.get('sock')
		if self.__pysock:
			
			# Need to keep these as private attributes
			# in case the socket is closed then opened
			# again.
			self.__family = self.__pysock.family
			self.__proto  = self.__pysock.proto 
			self.__type = self.__pysock.type
			
			try:
				# Better set this one first, I guess.
				self.__pysock.settimeout(self.__tmout)
				
				# This will throw an exception if 
				# socket is not connected. (Only 
				# connected sockets may be held in
				# a Socket object.
				addr = self.__pysock.getsockname()
				self.__connected = True
				
			except Exception:
				pass
		
		# Set the family, proto, and type for any socket
		# created by the create() or listen() method. Use
		# the sockval() classmethod to convert strings to
		# types (because strings are specified in config).
		if not self.__pysock:
			self.__family = sockval(c.get('family'), socket.AF_INET)
			self.__proto = sockval(c.get('proto'), 0)
			self.__type = sockval(c.get('type'), socket.SOCK_STREAM)
		
	
	
	
	def __del__(self):
		"""Shutdown; clear target."""
		try:
			self.shutdown()
		except:
			pass
		finally:
			self.__target = None
	
	
	@property
	def connected(self):
		"""
		True if connected, else False
		"""
		return True if self.__pysock and self.__connected else False
	
	
	@property
	def listening(self):
		"""
		True if listening, else False
		"""
		return True if self.__pysock and self.__listening else False
	
	
	@property
	def timeout(self):
		"""Timeout setting for this connection's socket.socket."""
		if self.__pysock:
			self.__tmout = self.__pysock.gettimeout()
		return self.__tmout
	
	@timeout.setter
	def timeout(self, timeout):
		"""Set timeout for this connection's socket.socket."""
		self.__tmout = timeout
		if self.__pysock:
			self.__pysock.settimeout(timeout)
	
	
	@property
	def ctimeout(self):
		"""Connection timeout."""
		self.__ctmout
	
	@ctimeout.setter
	def ctimeout(self, connectionTimeout):
		"""Set connect timeout."""
		self.__ctmout = connectionTimeout
	
	
	@property
	def bufsize(self):
		"""Read buffer size."""
		return self.__bufsz
	
	@bufsize.setter
	def bufsize(self, bufsize):
		self.__bufsz = bufsize
	
	
	@property
	def backlog(self):
		"""Server backlog value."""
		return self.__bklog
	
	
	@property
	def peer(self):
		"""
		The address of the remote connection, or None
		if not connected.
		"""
		return self.__pysock.getpeername() if self.connected else None
	
	
	@property
	def name(self):
		"""
		The address of the lockal socket, or None if
		not connected.
		"""
		return self.__pysock.getsockname() if self.connected else None
	
	
	@property
	def family(self):
		"""socket.family"""
		return self.__family 
	
	
	@property
	def proto(self):
		"""socket.proto"""
		return self.__proto
	
	
	@property
	def type(self):
		"""socket.type"""
		return self.__type
	
	
	
	
	#
	# TODO: Look into the kwargs limitations.
	#
		
		
	
	def shutdown(self, err=None):
		"""
		Shutdown and close the connection. 
		Sets self.__pysock to None.
		"""
		self.__connected = False
		self.__listening = False
		if self.__pysock:
			s = self.__pysock
			self.__pysock = None
			try:
				s.shutdown(socket.SHUT_RDWR)
			except Exception:
				pass
			try:
				s.close()
			except Exception:
				pass
	
	
	
	def send(self, data):
		"""
		Send given data immediately.
		"""
		if data:
			try:
				self.__pysock.send(data)
			except socket.timeout:
				pass
			except socket.error:
				self.shutdown()
				raise
			except Exception as ex:
				raise Exception('send-error', {'python':str(ex)})
	
	
	def sendlines(self, data, endl="\r\n"):
		"""
		Send lines one at a time with `endl` (default crlf) appended to 
		each.
		"""
		lines = data.splitlines()
		for d in lines:
			self.send("%s\r\n" % d)
	
	
	
	def recv(self):
		"""
		Return any received data, or None if no data has been received.
		If a target is set, sends received data to target.on_recv() rather
		than returning the data.
		"""
		if self.__pysock:
			try:
				# AS I UNDERSTAND IT..
				# It's rare but some systems don't support 
				# select.select(). That shouldn't stop us.
				try:
					# POLL - DON'T WAIT FOR TIMEOUT
					s = self.__pysock
					R,W,X = select.select([s],[],[s],0)
					if X:
						pass
					if not R:
						return None
				except Exception as ex:
					pass
				
				# receive
				d = self.__pysock.recv(self.__bufsz)
				if not d:
					self.shutdown()
				else:
					# For data that must be handled instantly.
					if self.__target:
						self.__target.on_recv(d)
					else:
						return d
			
			except socket.timeout:
				return None
			
			except socket.error as ex:
				errno = None if isinstance(ex, str) else ex[0]
				if errno in [10058,10054,10053]:
					# 10058: Recv attempt after peer disconnect.
					# 10054: Peer brutishly disconnected. (Server)
					# 10053: An existing connection was forcibly closed 
					#        by the remote host. (Client)
					self.shutdown(errno)
				else:
					raise
			except Exception:
				self.shutdown()
				raise
	
	
	
	def connect(self):
		"""
		Open connection to address given to constructor.
		"""
		if self.connected:
			raise Exception('already-connected', xdata())
		
		# create socket
		self.__pysock = socket.socket(
			self.__family, self.__type, self.__proto
		)
		
		# connect
		try:
			self.__pysock.settimeout(self.__ctmout)
			self.__pysock.connect((self.__host, self.__port))
			self.timeout = self.__tmout
			self.__connected = True
		except:
			self.__pysock = None
			raise
	
	
	# LISTEN
	def listen(self, *args, **kwargs):
		"""
		Server support. Listen for incoming connection requests.
		"""
		
		# create socket
		self.__pysock = socket.socket(self.__family, self.__type)
		self.__pysock.settimeout(self.__tmout)
		self.__pysock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.__pysock.bind((self.__host, self.__port))
		self.__pysock.listen(self.__bklog)
		self.__listening = True
	
	
	# ACCEPT
	def accept(self):
		"""
		Server support. Return the server-side socket for the connection.
		"""
		try:
			try:
				# POLL - DON'T WAIT FOR TIMEOUT
				# It's rare, but some systems don't support 
				# select.select. That shouldn't stop us.
				R,W,X = select.select([self.__pysock],[],[],0)
				if not R:
					return None
			except Exception:
				pass
			return self.on_accept(self.__pysock.accept())
		except socket.timeout:
			return None
	
	
	
	def on_accept(self, sa):
		if self.__target:
			return self.__target.on_accept(sa)
		return sa

