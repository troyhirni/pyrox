"""
Copyright 2016 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

HTML Parser - EARLY DEVELOPMENT - sort of works -; Please Comment.

parsehtml() requires unicode or bytes and encoding. It returns an 
HTMLDocument object, which supports subscripting, as do nodes.

There's still a long way to go, but I want a copy in the master.

#  Here's something from the interpreter.
>>> from x import html
>>> d = html.parsehtml(html.TEST) # returns document root.
>>> d[0]
<text:[2]>
>>> d[1]
<tag:html[3]>
>>> d[1][2][0].text
u'This is a test!'
>>>
"""

try:
	from html.parser import HTMLParser
except:
	from HTMLParser import HTMLParser

try:
	from pyrox.base import *
except:
	from base import *

from pyrox.base import text



def parsehtml(htmlstr, encoding=None):
	"""
	Pass html as unicode or bytes. Specify encoding if known, else an
	attempt is made to detect. Error is raised if encoding is neither
	specified nor detected.
	"""
	if not isinstance(htmlstr, unicode):
		if not encoding:
			encoding = text.Encoding(htmlstr).detect()
		if encoding:
			htmlstr = htmlstr.decode(encoding)
			
	p = ParseHTML(htmlstr)
	return HTMLDocument(p.doc, p.decl) 



#
# PARSER
#

class ParseHTML(HTMLParser):
	"""
	A DOM Tree HTML Parser. Puts unclosed tags under the next closing
	tag. Eg, "<A><b>1<b>2</A>" yields "<A><b>1</b><b>2</b></A>" rather
	than "<A><b>1<b>2</b></b></A>".
	
	I'm not sure whether this is correct. Is there one correct way to 
	parse semi-valid html?
	"""
	def __init__(self, htmlstr=None):
		"""Pass a unicode html string."""
		if not isinstance(htmlstr, unicode):
			raise Exception("html-no-encoding")
		
		HTMLParser.__init__(self)
		self.doc = []
		self.decl = []
		
		if htmlstr:
			self.feed(htmlstr)
	
	@property
	def last(self):
		return self.doc[-1]
	
	# CALLBACKS
	def handle_starttag(self, tag, attrs):
		self.doc.append(HTMLNode('tag', tag, attrs))
	
	def handle_endtag(self, tag):
		r = []
		try:
			# pop to the last doc.node matching 'tag'
			while self.last.nodename != tag:
				r.append(self.doc.pop())
		except IndexError:
			# unmatched end tag. ignore.
			self.doc.extend(r)
			return 
		
		# No node gets content until there's an end tag - then, the
		# currently ending node gets everything inside itself as
		# though each un-ended tag had been closed directly before its 
		# following tag.
		r.reverse()
		self.last.content = r
		
		# set the parent for each content node
		for n in r:
			n.setparent(self.last)
	
	def handle_startendtag(self, tag, attrs):
		self.handle_starttag(tag, attrs)
		#self.handle_endtag(tag) # should it do this???
	
	def handle_comment(self, data):
		self.doc.append(HTMLTextNode('comment', None, None, data))
	
	def handle_data(self, data):
		self.doc.append(HTMLTextNode('text', None, None, data))

	def handle_pi(self, data):
		self.doc.append(HTMLNode('pi', None, None, data))
	
	def handle_decl(self, decl):
		self.decl.append(decl.split(None, 1))
	
	def unknown_decl(self, data):
		self.decl.append(data.split(None, 1))



#
# DOCUMENT TREE
#

class HTMLObject(object):
	pass



class HTMLDocument(HTMLObject):
	def __init__(self, doc, decl):
		self.__doc = doc or []
		self.decl = decl or []
	
	def __getitem__(self, key):
		return self.__doc[key]
	
	def __len__(self):
		return len(self.__doc)



class HTMLNode (HTMLObject):
	def __init__(self, t, n, a, d=[]):
		self.nodetype = t
		self.nodename = n
		self.nodeattr = a
		self.content = d
		self.__parent = None
	
	def setparent(self, par):
		if self.__parent:
			self.__parent.remove(self)
		self.__parent = par
	
	def __getitem__(self, key):
		return self.content[key]
	
	def __repr__(self):
		#a = " %s" % (self.attrstring()).strip()
		return "<%s:%s[%s]>" % (self.type, self.name, len(self.content))
	
	def attrstring(self):
		if not self.nodeattr:
			return ''
		r = []
		for a in self.nodeattr:
			r.append('%s="%s"' % a)
		return ' '.join(r) if r else ''
	
	@property
	def type(self):
		return self.nodetype
	
	@property
	def name(self):
		return self.nodename
	
	@property
	def attrs(self):
		return self.nodeattr
	
	@property
	def children(self):
		return self.content



class HTMLTextNode(HTMLNode):
	
	def __str__(self):
		return self.text
	
	def __repr__(self):
		return "<%s:[%s]>" % (self.type, len(self.text))
	
	@property
	def text(self):
		return self.content
	
	@property
	def children(self):
		return []
		

#
# TEST HTML STRINGS (To be removed soon.)
#

TEST = u"""
	<html><head><title>Test!</title></head>
		<body>This is a test!</body></html>
"""

TEST2 = u"""
<a this="could be good">1
	<b>2
		<c>3
		<d>4
		5
	</b>
</a>
"""
# = <a>1<b>2<c>3<d>4</d>5</b></a>
# 1.[a,1,b,2,c,3,d,4...
# 2.[a,1,b,2,c,3,d[4],5...
# 3.[a,1,b[2,c,3,d[4],5]...
# = [a[1,b[2,c,3,d[4],5]]



