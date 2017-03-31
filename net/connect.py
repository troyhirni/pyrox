"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyro project, distributed under the terms 
of the GNU Affero General Public License.

CONNECT - Socket Connection (Built for TCP, but others may work)

Provides basic control over a connected client socket (given directly
or created by the createconnection classmethod) with recv, send, and
shutdown methods. Connect objects are intended for one-time use and
 become defunct after shutdown.
"""

from .socki import *
import select, struct



class Connect(Socket):
	
	# INIT
	def __init__(self, config=None, **k):
		"""
		There are several ways to create a Connect object:
		 1 - Pass a connected socket using keyword `sock`.
		 2 - Pass connection configuration arguments as a dict. Keyword 
		     args will update the dict.
		 3 - Pass connection url, which will be parsed to a dict that's
		     then updated with any given kwargs.
		
		When creating a connection with an already-connected socket (#1, 
		above), the Connect object will begin operation in a 'connected'
		state. If no `sock` keyword is found in kwargs or the config dict,
		then the Connect object's `connected` property will return False.
		
		NOTES: 
		 * Passing a defunct or disconnected socket will result in errors 
		   when used.
		 * Invalid config parameters are ignored.
		
		Valid connection parameter sets include:
		 - SET 1:
		   sock : a connected socket; when passed, all others are ignored.
		 
		 - SET 2:
		   host : the host name to connect to (4/6)
		   port : the port to connect to
		
		Other valid config parameters include:
		 bufsize : size of the read buffer in bytes (int, def=4096)
		 timeout : seconds for operational timeouts (float, def=0.0001)
		 ctimeout : seconds for connection timeout (float, def=20)
		"""
		# Store configuration (sets defaults).
		conf = self.parseconfig(config, **k)
		
		# store important values
		self.__bufsize = conf['bufsize']
		
		# not currently needed - handled by Socket class
		#self.__timeout = conf['timeout']
		#self.__ctimeout = conf['cbufsize']
		
		# Get or open the socket connection.
		if 'sock' in conf:
			self.__sock = conf['sock']
		else:
			self.__sock = self.createconnection(config, **k)
	
	
	@property
	def connected(self):
		return True if self.__sock else False
	
	
	# SEND
	def send(self, data):
		"""
		Send given data immediately.
		
		ERRORS (and how to handle them):
		 * socket.timeout : In the event of socket.timeout errors, retry
		   sending until you succeed or are ready to give up.
		 * socket.error : On socket.error exceptions, the socket is 
		   shutdown, so you have to reconnect and renegotiate the
		   transmition in whatever way is appropriate to your situation.
		 * For other exception types check the `python` xdata key for
		   clues to help debug the problem.
		"""
		if data:
			try:
				return self.__sock.send(data)
			except socket.timeout:
				raise
			except socket.error:
				self.shutdown()
				raise
			except Exception as ex:
				raise Exception('send-fail', xdata(reason='socket-send-error',
					python=str(ex)
				))
	
	
	# RECV
	def recv(self):
		"""
		Return any received data, or None if no data has been received.
		If a target is set, sends received data to target.on_recv() rather
		than returning the data.
		"""
		if self.__sock:
			try:
				try:
					# POLL - DON'T WAIT FOR TIMEOUT
					s = self.__sock
					R,W,X = select.select([s],[],[s],0)
					if X:
						pass
					if not R:
						return None
				except Exception as ex:
					# AS I UNDERSTAND IT..
					# It's rare but some systems don't support select.select().
					# That shouldn't stop us (though it will slow things down
					# a little).
					pass
				
				# receive
				d = self.__sock.recv(self.__bufsize)
				if not d:
					self.shutdown()
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
	
	
	# SHUTDOWN
	def shutdown(self):
		"""
		Close the connection.
		"""
		if self.__sock:
			s = self.__sock
			self.__sock = None
			try:
				s.shutdown(socket.SHUT_RDWR)
			except Exception:
				pass
			try:
				s.close()
			except Exception:
				pass





