"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

ADDRI - Address Info

Convenience utility for finding socket creation arguments.
"""

from . import socki
from .. import *

import socket


#
# ADDR-INFO
#
class AddrInfo(object):
	
	def __init__(self, config=None, **k):
		conf = config or {}
		conf.update(Base.kcopy(k, 'family type proto flags host port'))
		
		# allow values to be given by name, rather than value
		for x in 'family type proto'.split():
			if x in conf:
				conf[x] = socki.sockval(conf[x])
		
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
				family = socki.sockname(x.family, "AF_"),
				proto  = socki.sockname(x.type, "IPPROTO_"),
				type   = socki.sockname(x.type, "SOCK_"),
				flags  = x.flags
			)
	
	# DISPLAY
	def display(self, i=0):
		Base.ncreate('fmt.JDisplay').output(self.describe(i))


