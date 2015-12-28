"""
Copyright 2014-2015 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

Parse URLs; Retrieve and work with URL content.
"""


import encodings.aliases#, io


# default values; common functions/classes;
from ..base import *


# compensate for renamed symbols in python 3
class MM2(object):
	@classmethod
	def contenttype(cls, i): return i.gettype();
	@classmethod
	def maintype(cls, i): return i.getmaintype();
	@classmethod
	def subtype(cls, i): return i.getsubtype();
	@classmethod
	def param(cls, i, pname): return i.getparam(pname)

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
# CONVENIENCE FUNCTIONS
#
def parse(url):
	"""Parse url string and return dict containing parts."""
	return UParse.parse(url)


def open(url, *a):
	"""
	Returns a UResponse object for the given url.	Arguments are the 
	same as for urllib's urlopen() function.
	"""
	return UResponse(url, *a)









class UResponse(object):
	"""Response object for the url.open() function."""
	
	PMessage = None
	
	def __init__(self, *a):
		self.__file = urlreq.urlopen(*a)
		#self.__reader = io.BufferedReader(self.__file)
	
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
		try:
			return self.__charset
		except:
			c = self.param('charset')
			if not c: 
				c = self.__htmlfindcharset()
			self.__charset = c.replace('-','_').lower() if c else None
			return self.__charset
	
	# private
	def __htmlfindcharset(self):
		bb = self.content
		for e in ENCODINGS:
			try:
				top = bb.decode(e)
				try:
					p = HTMLCharsetParser()
					p.feed(top)
				except HTMLParseStop:
					return p.result.get('charset')
			except Exception as ex:
				pass


# Utility - to determine character sets in HTML files.
class HTMLCharsetParser(HTMLParser):
	"""
	Scan for content type.
	 - Parse to the meta tag that defines "content-type" or "charset"
	 - Set self.result to the charset
	 - Raise HTMLParseStop exception
	"""
	def handle_starttag(self, tag, attrs):
		"""Look for meta http-equiv content type."""
		if (tag.lower() == 'meta'):
			n = attrs[0][0].lower() # content-type or charset
			e = attrs[0][1].lower() # value
			if (n=='http-equiv') and (e=='content-type'):
				x = attrs[1][1].split(';')
				contype = x[0]
				charset = x[1].split('=')[1].strip() if len(x)>1 else None
				self.result = {'contents':contype, 'charset':charset}
				raise HTMLParseStop()
			elif (n=='charset'):
				self.result = {'charset':attrs[0][1]}
				raise HTMLParseStop()
	
	def handle_endtag(self, tag):
		"""Don't look past the html head section."""
		if tag == 'head':
			raise HTMLParseStop({})


class HTMLParseStop (Exception):
	"""This exception is raised to stop HTML parsing."""
	pass






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
		Split on ':' and return a tupel of at least two values, any of
		which may be None.
		"""
		x = s.split(':')
		if x:
			return (x[0],None) if len(x)==1 else tuple(x)
		return (None,None)




#
# ENCODINGS
#  - These are the available encodings as taken from python 
#    documentation.
#  - These may be moved to a JSON config file in the future.
#
ENCODINGS = [
	'ascii', 'big5', 'big5hkscs', 'cp037', 'cp424', 'cp437', 'cp500', 
	'cp720', 'cp737', 'cp775', 'cp850', 'cp852', 'cp855', 'cp856', 
	'cp857', 'cp858', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864', 
	'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 
	'cp950', 'cp1006', 'cp1026', 'cp1140', 'cp1250', 'cp1251', 
	'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 
	'cp1258', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr', 
	'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp', 'iso2022_jp_1', 
	'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3', 
	'iso2022_jp_ext', 'iso2022_kr', 'latin_1', 'iso8859_2', 
	'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7', 
	'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_13', 
	'iso8859_14', 'iso8859_15', 'iso8859_16', 'johab', 'koi8_r', 
	'koi8_u', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 
	'mac_latin2', 'mac_roman', 'mac_turkish', 'ptcp154', 'shift_jis', 
	'shift_jis_2004', 'shift_jisx0213', 'utf_32', 'utf_32_be', 
	'utf_32_le', 'utf_16', 'utf_16_be', 'utf_16_le', 'utf_7', 'utf_8', 
	'utf_8_sig'
]

# Extend encodings with all aliases for more potential matches.
ENCODINGS_ALIASES = []
ENCODINGS_ALIASES.extend(ENCODINGS)
ENCODINGS_ALIASES.extend(encodings.aliases.aliases)



