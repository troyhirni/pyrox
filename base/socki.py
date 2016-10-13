"""
SOCKET INFO


"""
import socket



#
# SOCK VAL
# - Get values from python's socket module.
#
def sockval(name):
	"""
	Returns the value of anything defined in python's socket module given
	the `name` for that value. For example, given a `name` of "SHUT_RDWR", 
	the value of socket.SHUT_RDWR is returned (as an integer).
	
	Any kind of value `name` that's defined in the socket module will be 
	returned, but the intention here is to suport the passing of constant
	values given as strings in config dict arguments. That is, it's much
	easier to pass socktype='SOCK_STREAM' rather than looking up the value
	of socket.SOCK_STREAM and entering that integer instead.
	
	If `name` is not defined in the socket module, then its value will be
	returned as-is. This makes it possible to pass either 'SOCK_STREAM' or
	socket.SOCK_STREAM as the value of config['socktype'].
	"""
	if val and (val in socket.__dict__):
		val = socket.__dict__[val]
	return val


def sockname(value, prefix=None):
	"""
	Searches for names that define the given `value` in python's socket
	module. Pass `prefix` (a string) to limit the results.
	"""
	r = []
	l = len(prefix)
	for k in socket.__dict__:
		if (not l) or (k[:l] == prefix):
			if socket.__dict__[k] == value:
				r.append(k)
	return r



# TEMPORARY - REMOVE SOON
def printx(prefix=''):
	iPrefixLen = len(prefix)
	for k in dir(socket):
		if (iPrefixLen==0) or (k[:iPrefixLen] == prefix):
			print ("%s : %s" % (k, str(socket.__dict__[k])))





#
# SOCK INFO
#
class SockInfo(object):
	"""
	Immutable addressing info for creation of socket objects.
	"""
	def __init__(self, config={}, **k):
		"""
		Pass a config dict (and/or kwargs) containing host, port, family, 
		socktype, proto, and flags, as needed.
		
		
		All values may be passed as either:
		 * a direct (integer) value as defined in the socket module, OR...
		 * a string matching the defined name of a constant from the
		   socket module.
		
		REQUIRED KEY:
		 * port: There's no getting around specification of a 'port' value.
		         It may be specified by protocol (eg. 'http') or by integer,
		         but absolutely must be supplied. 
		
		DEFAULT KEY VALUES:
		 * host: defaults to socket.gethostname()
		
		OTHER DEFAULTS:
		The family, socktype, proto, and flags values are optional. If not
		specified, the first result as returned by socket.getaddrinfo() will
		provide the defaults.
		"""
		config.update(k)
		self.conf = config
		
		# TOP CONFIG VALUES (HOST/PORT)
		host = config.get('host')
		host = host if host else socket.gethostname()
		port = config['port'] # REQUIRED!
		
		# LIST ADDRESS-INFO CHOICES
		self.__addrinfo = socket.getaddrinfo(host, port)
		if not len(self.__addrinfo):
			raise Exception('socket-params-invalid', 'no-matching-address')
		
		# STORE BEST ADDRESS
		self.__addr0 = self.__addrinfo[0]
		self.__addr = self.__addr0[4] # (host,port)
		self.__host = self.__addr[0]
		self.__port = self.__addr[1]
		self.__family = self.__addr0[0]
		self.__socktype = self.__addr0[1]
		self.__proto = self.__addr0[2]
		self.__cname = self.__addr0[3] # canonname
		
		# FLAGS
		flags = []
		cflags = config.get('flags', [])
		cf = cflags if isinstance(cflags, list) else cflags.split()
		for f in cf:
			flags.append(sockval(f))
		self.__flags = flags
	
	
	#
	# VALUES
	#
	@property
	def addr(self):
		"""Return (host,port) as tupel"""
		return self.__addr
	
	@property
	def port(self):
		"""Return port as integer"""
		return self.__port
	
	@property
	def host(self):
		"""Return host"""
		return self.__host
	
	@property
	def cname(self):
		"""Return canonical name"""
		return self.__cname
	
	@property
	def family(self):
		"""Return the defined integer family integer value."""
		return self.__family
	
	@property
	def nfamily(self):
		"""Return the address-family name as defined in socket module."""
		try:
			return self.__nfamily
		except:
			try:
				self.__nfamily = sockname(self.family, "AF_")
			except:
				self.__nfamily = None
			return self.__nfamily
	
	@property
	def socktype(self):
		"""Return the defined integer socket type integer value."""
		return self.__socktype
	
	@property
	def nsocktype(self):
		"""Return the socket type name as defined in socket module."""
		try:
			return self.__nsocktype
		except:
			try:
				self.__nsocktype = sockname(self.socktype, "SOCK_")
			except:
				self.__nsocktype = None
			return self.__nsocktype
	
	@property
	def proto(self):
		"""Return the defined integer protocol value."""
		return self.__proto
	
	@property
	def nproto(self):
		"""Return the socket protocol as defined in socket module."""
		try:
			return self.__nproto
		except:
			try:
				self.__nproto = sockname(self.proto, "IPPROTO_")
			except:
				self.__nproto = None
			return self.__nproto
	
	@property
	def flags(self):
		return self.__flags
	
	
	#
	# INFO
	#
	@property
	def addrinfo(self):
		"""
		Returns a list of possible connection parameters matching this
		object's config. Each item is a set containing:
			(family, socktype, proto, canonname, sockaddr)
		
		Only the first item in this list is used to set this object's 
		properties. To use a different item from the list, directly specify
		all socket-related config options when creating the object.
		"""
		return self.__addrinfo
	
	@property
	def addr0(self):
		"""
		Returns the full address-info tupel used to build this socket info
		object's properties.
		"""
		return self.__addr0
	
	@property
	def fqdn(self):
		"""Return fully qualified domain name."""
		try:
			return self.__fqdn
		except:
			self.__fqdn = socket.getfqdn(self.host)
			return self.__fqdn
	
	@property
	def hostname(self):
		try:
			return self.__hostname
		except:
			self.__hostname = socket.gethostbyname(self.host)
			return self.__hostname
	
	@property
	def hostex(self):
		try:
			return self.__hostex
		except:
			self.__hostex = socket.gethostbyname_ex(self.host)
			return self.__hostex





#
# SOCK TASK
#
class SockTask(Task):
	
	def __init__(self, config={}, **k):
		Task.__init__(self, config, **k)
		self.__sockinfo = SockInfo(config)
		
		# create the socket onOpen()
		self.__socket = None
	
	@property
	def active(self):
		return True if self.__socket else False
	
	@property
	def socket(self):
		return self.__socket
	
	@property
	def info(self):
		return self.__sockinfo
	
	def onOpen(self):
		si = self.info
		self.__socket = socket.socket(si.family, si.socktype, si.proto)
	
	def onClose(self):
		if self.__socket:
			try:
				self.__socket.close()
			finally:
				self.__socket = None


#
# CLIENT
#
class Client(SockTask):
	
	def onOpen(self):
		SockTask.onOpen(self)
		self.socket.connect(self.info.addr)
	
	def send(self, data):
		try:
			return self.socket.send(data)
		except Exception as ex:
			self.close()
		return None
		
	def recv(self, size=4096):
		return self.socket.recv(size)




#
# SERVER
#
class Server(SockTask):
	
	def __init__(self, config, **k):
		SockTask.__init__(self, config, **k)
		self.host = config['host']
		self.port = config['port']
		self.reuse = config.get('reuse', True)
		self.timeout = config.get('timeout', 0.0001)
		self.sessions = {}
	
	def io(self):
		try:
			si = self.info
			self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.socket.settimeout(self.timeout)
			self.socket.bind(si.addr)
			self.listen()
			
		except:
			pass
			
	
	def onClose(self):
		if self.socket:
			self.socket.close()
			self.socket = None
	
	def listen(self):
		
		# create socket
		self.socket.listen(self.__bklog)
		self.__listening = True





