"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

Parse URLs; Retrieve and work with URL content.
"""

# fmt imports * from .. too, so everything's here.
# from ..fmt import *  # IS THIS NEEDED?
# from ..data import text
from .. import *



# compensate for renamed symbols in python 3
class MM2(object):
	@classmethod
	def contenttype(cls, i): return i.gettype();
	@classmethod
	def maintype(cls, i): return i.getmaintype();
	@classmethod
	def subtype(cls, i): return i.getsubtype();
	@classmethod
	def param(cls, i, pname): return i.get(pname)#.getparam(pname)

class MM3(object):
	@classmethod
	def contenttype(cls, i): return i.get_content_type(); 
	@classmethod
	def maintype(cls, i): return i.get_content_maintype();
	@classmethod
	def subtype(cls, i): return i.get_content_subtype();
	@classmethod
	def param(cls, i, pname): return i.get_param(pname)


try:
	import urllib2 as urlreq
	import urlparse
	from HTMLParser import HTMLParser
	MessageMerge = MM2

except:
	import urllib.request as urlreq
	from urllib import parse as urlparse
	from html.parser import HTMLParser
	MessageMerge = MM3



#
# FUNCTIONS
#

def parse(url):
	"""Parse url string and return dict containing parts."""
	return UParse.parse(url)


def open(url, *a, **k):
	"""
	Returns a UResponse object for the given url. Arguments are the 
	same as for urllib's urlopen() function.
	
	from net import url
	r = url.open(someUrl)
	"""
	return UResponse(url, *a, **k)


def head(url):
	"""
	Returns a UResponse with just the head for the given url.
	
	from net import url
	h = url.head(someUrl)
	print (h.info())
	"""
	request = urlreq.Request(url)
	request.get_method = lambda : 'HEAD'
	return UResponse(request)





#
# URL - DOWNLOAD
#

class UResponse(object):
	"""Response object for the url.open() function."""
	
	PMessage = None
	
	def __init__(self, *a, **k):
		self.__file = urlreq.urlopen(*a, **k)
	
	def geturl(self):
		"""The actual URL of the resource retrieved."""
		return self.__file.geturl()
	
	def getcode(self):
		"""Response code."""
		return self.__file.getcode()
	
	def info(self):
		"""Message objects, as returned by python's urlopen()."""
		try:
			return self.__info
		except:
			self.__info = self.__file.info()
			return self.__info
	
	# INFO
	def param(self, name):
		"""Param, as from the info Message object."""
		return MessageMerge.param(self.info(), name)
	
	@property
	def content(self):
		try:
			return self.__content
		except:
			self.__content = self.__file.read()
			return self.__content
	
	@property
	def contenttype(self):
		"""The content type, as given by 'info'."""
		return MessageMerge.contenttype(self.info())

	@property
	def maintype(self):
		"""The main type, as given by 'info'."""
		return MessageMerge.maintype(self.info())

	@property
	def subtype(self):
		"""The sub-type, as given by 'info'."""
		return MessageMerge.subtype(self.info())
	
	@property
	def charset(self):
		"""
		Returns the specified charset as detected from BOM, in HTTP 
		headers, or a content specification (eg, meta tag) - in that
		order.
		"""
		try:
			return self.__charset
		except:
			e = Base.ncreate('data.text.Encoded', self.content)
			c = e.testbom()
			if not c:
				c = self.param('charset')
			if not c:
				bb = Base.ncreate('data.text.Encoded', self.content)
				c = bb.detect()
			self.__charset = e.pythonize(c)
			return self.__charset





#
# URL - PARSING
#

class UParse(object):
	"""
	URL Parsing.
	NOTE: This class is under construction. I hope to make it
				extendable so as to allow special handling of spceialized 
				schema as required.
	"""
	
	@classmethod
	def parse(cls, s):
		"""Parse url string 's' and return url parts as a dict."""
		R = {'url':s}
		x = urlparse.urlparse(s)
		s,n,p,q,f = x.scheme, x.netloc, x.path, x.query, x.fragment
		
		"""
		# <experimental>
		if s and not p: 
			try:
				p = socket.getservbyname(s)
			except:
				pass
		elif p and not s: 
			try:
				s = socket.getservbyport(p)
			except:
				pass
		# </experimental>
		"""
		
		R.update(dict(scheme=s, netloc=n, path=p, query=q, fragment=f))
		R.update(cls.authority(x.netloc))
		return R
	
	@classmethod
	def authority (cls, s):
		"""
		Splits string in format of "username:password@host:port" and 
		returns a dict containing those parts. The 'host' part is 
		required. If included, the 'port' will be cast as an integer.
		"""
		if s:
			a = s.split('@')
			if len(a) == 2: # user:pass@host:port
				host,port = cls.authsplit(a[1])
				user,pswd = cls.authsplit(a[0])
			elif len(a) == 1: # host:port only
				host,port = cls.authsplit(a[0])
				user,pswd = (None,None)
			try:
				if port:
					port = int(port)
				return dict(host=host,port=port,username=user,password=pswd)
			except:
				pass
		return dict(host=None,port=None,username=None,password=None)
	
	@classmethod
	def authsplit(cls, s):
		"""
		Split on ':' and return a tuple of at least two values, any of
		which may be None.
		"""
		x = s.split(':')
		if x:
			return (x[0],None) if len(x)==1 else tuple(x)
		return (None,None)


