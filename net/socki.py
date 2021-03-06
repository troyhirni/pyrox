"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

SOCKI - SOCKET INFO

Convenience utility for finding socket creation arguments.
"""

from .. import *
import socket


# GLOBALS (DEFAULTS)
SOCKWRAP_BUFSIZE = 4096
SOCKWRAP_TIMEOUT = 0.0001
SOCKWRAP_CTIMEOUT = 20



# SOCK VAL
# - Get values from python's socket module.
def sockval(name):
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


# SOCK-NAME
def sockname(value, prefix=None):
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





#
# EXPERIMENTAL
#
class Socket(object):
	
	@classmethod
	def parseurl(cls, url):
		"""
		Socket-based classes will accept a url as `config`.
		"""
		try:
			return cls.__parseurl(url)
		except:
			cls.__parseurl = TFactory(Base.innerpath('net.url.parse')).type
			return cls.__parseurl(url)
	
	
	@classmethod
	def configdefaults(cls, configDict):
		"""Set config default values."""
		configDict.setdefault('bufsize', SOCKWRAP_BUFSIZE)
		configDict.setdefault('timeout', SOCKWRAP_TIMEOUT)
		configDict.setdefault('ctimeout', SOCKWRAP_CTIMEOUT)
		configDict.setdefault('backlog', socket.SOMAXCONN) #for servers
		return configDict
	
	
	@classmethod
	def parseconfig(cls, config=None, **k):
		"""Gather configuration params with default settings."""
		conf = config or {}
		try:
			# if config is dict...
			conf.update(k)
		except AttributeError:
			# if config is a url str...
			conf = cls.parseurl(conf)
			conf.update(k)
		
		# make sure defaults are set
		return cls.configdefaults(conf)
	
	
	@classmethod
	def createconnection(cls, config=None, **k):
		"""Return a socket given a full configuration dict."""
		# read config
		conf = cls.parseconfig(config, **k)
		address = (conf['host'], conf['port'])
		
		# create socket
		ctimeout = conf.get('ctimeout', SOCKWRAP_CTIMEOUT)
		sock = socket.create_connection(address, ctimeout)
		
		# set common options and return
		sock.settimeout(conf.get('timeout', SOCKWRAP_TIMEOUT))
		return sock

























