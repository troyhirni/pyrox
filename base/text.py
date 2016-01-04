"""
Copyright 2014-2015 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

Text (and support for Encoded bytes). 
"""

try:
	from ..base import *
except:
	from base import *

import codecs, sys, unicodedata as ucd

try:
	from html.parser import HTMLParser
except:
	from HTMLParser import HTMLParser




def text(text, encoding=DEF_ENCODE, **k):
	"""
	Returns a Text object given unicode or bytes and a valid encoding.
	If bytes are given, encoding defaults to DEF_ENCODE (UTF-8).
	"""
	return Text(text, encoding, **k)



#
# TEXT
#
class Text(object):
	"""
	Represents text. Stores a unicode string and an encoding. Use the
	text property to get the unicode value, or bytes to return the
	encoded bytes.
	"""
	
	def __init__(self, text, encoding=None, **k):
		"""
		Pass text as unicode or byte string. Optional kwargs are applied
		when encoding/decoding. Keyword 'encoding' applies to the bytes 
		property result.
		
		See set() help for details.
		"""
		self.set(text, encoding, **k)
	
	
	@property
	def encoding (self):
		"""The encoding associated with this text."""
		return self.__enc
	
	@property
	def text (self):
		"""The unicode text string object."""
		return self.__text
	
	@property
	def bytes (self):
		"""Returns bytes encoded using self.encoding."""
		return self.text.encode(self.encoding)
	
	# ENCODE
	def encode(self, encoding=None, **k):
		"""Encodes this text as bytes, applying any kwargs."""
		return self.text.encode(encoding)
	
	# SET
	def set(self, x, encoding=None, **k):
		"""
		Pass a unicode string or bytes. Optionally, specify encoding by 
		keyword and it will be used to decode bytes (if bytes were 
		passed to the constructor), and (always) to encode text for the
		bytes property.
		
		If you pass a byte string but don't specify an encoding, a weak
		attempt is made to detect the encoding. If that fails, an
		exception is raised.
		
		CAUTION: Always specify the encoding for bytes if you know it. 
		         Encode.detect() is not comprehensive and will often 
		         return None. See help for Encode for details.
		"""
		if isinstance(x, unicode):
			# It's unicode text, so just store the encoding (for use by
			# the bytes property) and store the unicode text.
			self.__enc = encoding or DEF_ENCODE
			self.__text = x
		else:
			if encoding:
				# Bytes and encoding were given, so decode to text.
				self.__enc = encoding or DEF_ENCODE
				self.__text = x.decode(self.__enc, **k)
			else:
				# No encoding was specified, so try to detect.
				ee = Encoded(x)
				de = ee.detect()
				if not de:
					raise Exception('text-encoding-needed')
				self.__enc = de
				self.__text = ee.bytes.decode(self.__enc, **k)
	


#
# ENCODED
#
class Encoded(object):
	"""
	Attempts to detect encoding of raw bytes strings. This is not yet
	a comprehensive detection system. I've still got a lot to learn :)
	
	~~~ PROBLEMS WITH THE decode() METHOD? READ THE FOLLOWING ~~~
	
	The decode() method works by first looking for a BOM and then, if
	that fails, looking for a hint in the text itself. 
	
	NOTES:
	 * The testbom() method WILL NOT WORK unless your bytestring
	   actually has a BOM at the head of it. This is pretty useful for
	   downloaded files, but most file system files neither start with
	   a BOM nor specify an encoding in the text (and even those that
	   do specify an encoding in the text may not be covered here!)
   * The testspec() function totally relies on text files to specify
     an encoding in the text file. Eg, <!SOMETAG charset=utf-8>. If
     no such specification exists, testspec() is useless.
   * Calling bomremove() wipes out your ability to use testbom(), 
     so detect first, remove BOM later!
   * Modern HTML files usually specify an encoding, but HTML coders
     sometimes fail to get it right. I've seen plenty of charset
     attributes that don't match any real encoding name.
  
  Apart from all that, this seems like at least a good start. If you
  know me, be kind enough to make comments and suggestions! Thanks.
	"""
	
	def __init__(self, bbytes):
		"""Pass encoded byte strings."""
		self.__bb = bbytes
	
	@property
	def bytes(self):
		return self.__bb
	
	@classmethod
	def pythonize(cls, e):
		"""
		Replace '-' with '_' to match python encoding specifiers. 
		If not in ENCODINGS_ALIASES, remove '-' and try that.
		If that fails, return the original.
		"""
		p = e.lower().replace('-', '_')
		if p in ENCODINGS_ALIASES:
			return p
		p = p.replace('_', '')
		if p in ENCODINGS_ALIASES:
			return p
		return e
	
	def bomremove(self):
		"""
		Return the bytes after any byte order marks. 
		BE AWARE: After calling this there's no way to testbom(), so
		          be sure to get your encoding first.
		"""
		if self.__bb[:4] in [codecs.BOM_UTF32_BE, codecs.BOM_UTF32_LE]:
			self.__bb = self.__bb[4:]
		if self.__bb[:2] in [codecs.BOM_UTF16_BE, codecs.BOM_UTF16_LE]:
			self.__bb = self.__bb[2:]
		if self.__bb[:3] in [codecs.BOM_UTF8]:#, '\x2b\x2f\x76']:#utf-8/7
			self.__bb = self.__bb[3:]
	
	def detect(self):
		"""
		Attempts to detect a valid encoding for bytes based on BOM, 
		'charset' or 'encoding' specification in the text,
		"""
		# Give it a try... testbom() is very fast, but only
		# catches a few encodings.
		e1 = self.testbom()
		if e1:
			return e1
		
		# Look for specification from the text. This is relatively fast
		# when it works, but could cause Exceptions. Just ignore them
		# and move on.
		try:
			e2 = self.testspec()
			if e2 and e2 in ENCODINGS_ALIASES:
				return e2
		except:
			pass
		
		# Last ditch effort - look for html-style specification in
		# any encoding.
		e3 = self.testhtml()
		if e3 and e3 in ENCODINGS_ALIASES:
			return e3
		
		# This information could still be useful, so return the 
		# first-found result even if it's not in ENCODINGS_ALIASES. .
		return e1 or e2 or e3
	
	
	# TEST LIST
	def testlist (self, encodings=None):
		"""
		Attempts to decode then reencode byte string argument for each
		known encoding; Returns a list of successful matches. Set the
		encodings argument as a list to limit encodings tested; Default
		is base.ENCODINGS, which lists all documented encodings.
		
		Use this when searching manually for encodings that might work.
		
		HINT:
		Variety helps narrow the list, so pass the entire byte string.
		Check each matching encoding visually to see which gives correct 
		results.
		"""
		r = []
		for e in encodings or ENCODINGS:
			try:
				bb_dec = self.__bb.decode(e)
				bb_enc = bb_dec.encode(e)
				if bb_enc == self.__bb:
					r.append(e)
			except UnicodeError:
				pass
		return r
	
	# TEST BOM
	def testbom(self):
		"""
		Detect encoding based on byte order mark. Works only for UTF-32,
		UTF-16, UTF-8, gb18030, and UTF-7.
		"""
		
		# try the u32 encodings
		if self.__bb.startswith(codecs.BOM_UTF32_LE):
			return 'utf_32_le'
		elif self.__bb.startswith(codecs.BOM_UTF32_BE):
			return 'utf_32_be'
		
		# try the u16 encodings
		elif self.__bb.startswith(codecs.BOM_UTF16_LE):
			return 'utf_16_le'
		elif self.__bb.startswith(codecs.BOM_UTF16_BE):
			return 'utf_16_be'
		
		# utf-8
		elif self.__bb.startswith(codecs.BOM_UTF8):
			return 'utf_8_sig' #_sig? check this!
		
		# gb-18030
		elif self.__bb.startswith("\x84\x31\x95\x33"):
			return 'gb18030'
		
		# utf-7
		elif self.__bb.startswith('\x2b\x2f\x76'):
			b45 = self.__bb[3:5]
			if b45[0] in ["\x38","\x39","\x2b","\x2f"] or b45=="\x38\x2d":
				return 'utf-7'
		
		return None
	
	# TEST SPECIFICATION
	def testspec(self):
		"""
		Test for the specification of an encoding in the form of:
		 * charset = "<encoding>"
		 * encoding = "<encoding>"
		 * coding = "<encoding>"
		
		Whitespace, assignment operators, and literal delimiters
		are optional.
		"""
		# dump multi-byte zero-padding of ascii characters
		bb = self.__bb.replace("\0", "")
		
		# look for charset, coding (or encoding)
		for kw in ['charset', 'encoding', 'coding']:
			x = self.__bb.find(kw)
			if not x < 0:
				
				# start at the keyword kw
				p = x+len(kw)
				
				# ignore separation text
				ignore = '\t :=\'"'
				while self.__bb[p] in ignore:
					p = p + 1
				
				# get the prize
				r = []
				while not self.__bb[p] in ignore:
					r.append(self.__bb[p])
					p = p + 1
				
				e = self.pythonize(''.join(r))
				return e
	
	
	# TEST HTML
	def testhtml(self):
		"""Test for HTML-style charset specification."""
		try:
			p = HTMLCharsetParser()
			p.feed(txt)
		except HTMLParseStop:
			return p.result.get('charset')
		except:
			for e in ENCODINGS:
				try:
					txt = self.__bb.decode(e)
					try:
						p = HTMLCharsetParser()
						p.feed(txt)
					except HTMLParseStop:
						return self.pythonize(p.result.get('charset'))
				except Exception as ex:
					pass




class HTMLCharsetParser(HTMLParser):
	"""
	Scan for content type.
	 - Parse to the meta tag that defines "content-type" or "charset"
	 - Set self.result as dict containing charset key/value pair.
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
	"""Raise this to stop HTML parsing."""
	pass
