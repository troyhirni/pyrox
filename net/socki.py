"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

SOCKI - SOCKET INFO

Convenience utility for finding socket creation arguments.
"""

from .. import *
import socket



class AddrInfo(object):
	def __init__(self, config=None, **k):
		conf = config or {}
		conf.update(Base.kcopy(k, 'family type proto flags host port'))
		if not 'host' in conf:
			conf['host'] = socket.gethostname()
		
		# EXPERIMENTAL!
		# This allows values to be given by name, rather than value. I'm
		# not sure how valuable this is right now, but if it seems helpful
		# it might stay.
		for x in 'family type proto'.split():
			if x in conf:
				conf[x] = self.sockval(conf[x])
		
		# GET INITIAL ADDRESS INFO
		self.__addrinfo = socket.getaddrinfo(**conf)
	
	def __len__(self):
		return len(self.__addrinfo)
	
	def __getitem__(self, key):
		x = self.__addrinfo[key]
		f = x[3] if x[3] else 0 
		config = dict(
			family = x[0], type = x[1], proto= x[2], flags = f,
			host = x[4][0], port = x[4][1]
		)
		return AddrInfo(config)
	
	def get(self, i=0):
		return self.__addrinfo
	
	@property
	def family(self):
		return self.__addrinfo[0][0]
	
	@property
	def type(self):
		return self.__addrinfo[0][1]
	
	@property
	def proto(self):
		return self.__addrinfo[0][2]
	
	@property
	def flags(self):
		return self.__addrinfo[0][3]
	
	@property
	def addr(self):
		return self.__addrinfo[0][4]
	
	@property
	def host(self):
		return self.__addrinfo[0][4][0]
	
	@property
	def port(self):
		return self.__addrinfo[0][4][1]
	
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
	
	
	# DESCRIBE
	def describe(self, i=0):
		x = self[i] if i else self
		return dict(
				host   = x.host,
				port   = x.port,
				family = self.sockname(x.family, "AF_"),
				proto  = self.sockname(x.type, "IPPROTO_"),
				type   = self.sockname(x.type, "SOCK_"),
				flags  = x.flags
			)
	
	# DISPLAY
	def display(self, i=0):
		Base.ncreate('fmt.JDisplay').output(self.describe(i))
	
	
	#
	# SOCK VAL
	# - Get values from python's socket module.
	#
	@classmethod
	def sockval(cls, name):
		"""
		Returns the value of anything defined in python's socket module 
		given the `name` for that value. For example, given a `name` of 
		"SHUT_RDWR", the value of socket.SHUT_RDWR is returned (as an 
		integer).
		
		Any kind of value `name` that's defined in the socket module will
		be returned, but the intention here is to suport the passing of 
		constant values given as strings in config dict arguments. That 
		is, it's much easier to pass socktype='SOCK_STREAM' rather than 
		looking up the value of socket.SOCK_STREAM and entering that 
		integer instead.
		
		If `name` is not defined in the socket module, then its value will
		be returned as-is. This makes it possible to pass either the value
		itself or it's name, eg., 'SOCK_STREAM' or socket.SOCK_STREAM.
		"""
		if name and (name in socket.__dict__):
			# either `name` is a name defined in the socket module, or...
			x = socket.__dict__[name]
		else:
			# ... the actual value was given as `name`.
			x = name
		return x
	
	@classmethod
	def sockname(cls, value, prefix=None):
		"""
		Searches for names that define the given `value` in python's 
		socket module. Pass `prefix` (a string) to limit the results.
		"""
		r = []
		l = len(prefix) if prefix else 0
		for k in socket.__dict__:
			if (not l) or (k[:l] == prefix):
				if socket.__dict__[k] == value:
					r.append(k)
		return r
	