"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

DOM - Case-insensitive html parsing into a dom node structure

Named `dom` for the (partial) dom implementation, but probably does
not deserve it since parsing is based on the HTMLParser class and
therefore is case-insensitive. Despite that, the parse(html) function
does provide a complete (if somewhat difficult to use) list of nodes
with properties and methods prescribed by the DOM.

I'm considering the possibility of creating a custom parser so that
xml data can be safely imported. Until then...

PLEASE BE AWARE: Parsing is case-insensitive and DOES NOT enforce 
                 any DOM rules for closing tags, etc... This is only
                 a tool for importing HTML data. 
                 
                 YOU MUST EXAMINE THE DATA to make sure there are no
                 tag/attribute names that conflict because of case or
                 other unenforced DOM rules.
"""

try:
	from html.parser import HTMLParser
except:
	from HTMLParser import HTMLParser

from xml.dom import Node as TPythonNode

from .. import *



DOMString = unicode



def parse(html=None, **k):
	"""
	Case-insensitive html parsing. 
	"""
	if 'file' in k:
		mm = Base.ncreate('fs.mime.Mime', k['file'])
		f = mm.file()
		if not f:
			raise Exception('file-not-created')
		n = k.get('name')
		
		html = f.read(n) if n else f.read()
	else:
		_data = html
	
	# decode if 'encoding' kwarg is specified
	if 'encoding' in k:
		_data = _data.decode(k['encoding'])

	return Parse(unicode(html)).doc






class crawler(object):
	"""
	what's happening here isn't quite what I want. i want to try to 
	avoid recursion.
	
	THE LIST
	i want a list that grows, containing each parent - push when 
	entering a child, again when entering the child's child, again for
	the grandchild's child... pop when finished with a node's siblings,
	and stop when the last node's popped from the list.
	
	THE FUNCTION
	I want to pass crawler a function to which each node is applied; 
	this funciton will have access to the ancestry to help it decide
	which nodes to select for the result list.
	
	THE RESULT LIST
	A private result list should make its append method available so
	each time the function matches, a node can be appended. 
	"""
	def __init__(self, node):
		# current node
		self.__node = node
		
		# positions
		self.__start = node
		self.__child = node
		self.__sibling = node
	
	
	# CURRENT
	@property
	def node(self):
		return self.__node
	
	@property
	def info(self):
		return self.__node._xinfo()
	
	# 
	def next(self):
		c = self.node.nextChild()
		if c:
			self.__node = c
	
	def __childcrawl(self):
		rr = []
		child = self.__current.firstChild
		while child:
			rr.append(child._xinfo())
			child = child.nextSibling()
		return rr
	
	def crawl(self):
		if not self.__current:
			raise StopIteration()
		rr = [node._xinfo()]
		rr.extend(self.__childcrawl())
		self.__siblingcrawl()
		
	



class Parse(HTMLParser):
	
	def __init__(self, htmlstr=None):
		HTMLParser.__init__(self)
		
		self.decl = [] # DocType plus other declarations
		self.root = RootElement()
		self.doc = Document(self.root, self.decl)
		
		# accumulate nodes inside unclosed elements
		self._acum = []
		
		# if string was provided, parse it
		if htmlstr:
			self.feed(htmlstr)
		
		for n in self._acum:
			self.root.appendChild(n)
	
	
	def handle_starttag(self, tag, attrs):
		# Append unclosed nodes to a list. They become children of an
		# element once that element is closed (or parsing ends).
		self._acum.append(Element(tag, attrs))
	
	def handle_startendtag(self, tag, attrs):
		self.handle_starttag(tag, attrs)
	
	def handle_endtag(self, tag):
		r = []
		try:
			# pop to the last unclised _acum node matching 'tag'
			current = self._acum[-1]
			while (current.nodeName != tag) or (current._closed):
				r.append(self._acum.pop())
				current = self._acum[-1]
			r.reverse()
		except IndexError:
			# unmatched end tag. ignore.
			r.reverse()
			self._acum.extend(r)
			return 
		
		# now there's a list of nodes to add to the closing tag
		for n in r:
			self._acum[-1].appendChild(n)
		
		# mark the closing tag as closed
		self._acum[-1]._closed = 1
		
	
	def handle_comment(self, data):
		self._acum.append(Comment(data))
	
	def handle_data(self, data):
		self._acum.append(Text(data))

	def handle_pi(self, data):
		target, data = data.split(None,1)
		self._acum.append(ProcessingInstruction(target, data))
	
	def unknown_decl(self, data):
		if data.find("CDATA[") == 0:
			self._acum.append(CDATASection(data[6:]))
		else:
			self._acum.append(Comment("UNKNOWN DECL: %s" % data))
	
	def handle_decl(self, decl):
		self.decl.append(decl.split(None, 1))





class Node(object):
	def __init__(self, parent=None):
		self._closed = None
		self.__parent = parent
		#self.__document = parent.document if parent else None
	
	def _setparent(self, par):
		if self.__parent and (self.__parent != par):
			self.__parent.remove(self)
		self.__parent = par
	
	def __repr__(self):
		return "<%s>" % (self.nodeName)
	
	@property
	def nodeValue(self):
		return None
	
	@property
	def parentNode(self):
		return self.__parent
	
	@property
	def ownerElement(self):
		return self.__parent
	
	@property
	def ownerDocument(self):
		"""Returns the root element (document object) for a node."""
		try:
			return self.ownerElement.ownerDocument
		except:
			return None
	
	def isSameNode(self, other):
		return id(self) == id(other)
	
	# False None Pass
	@property
	def nodeValue(self):
		return None
	
	@property
	def childNodes(self):
		return tupel()

	def hasAttributes(self):
		return False
	
	def hasChildNodes(self):
		return False

	# Are these supposed to be in Node? It sure helps to have them...
	@property
	def firstChild(self):
		return None
	
	@property
	def lastChild(self):
		return None
	
	@property
	def previousSibling(self):
		return None
	
	@property
	def nextSibling(self):
		return None
	
	def _prevchild(self, n):
		return None
	
	def _nextchild(self, n):
		return None
	
	# EXPERIMENTAL
	def _xinfo(self):
		return dict(T=type(self), type=self.nodeType, name=self.nodeName,
			attr=self.attributes if self.hasAttributes else {}
		)





#
# E-NODE - For small extra non-DOM features
#
class ENode (Node):
	def __call__(self, tagname):
		r = []
		for c in self.childNodes:
			if c.nodeName == tagname:
				r.append(c)
		return r





#
# DOCUMENT - This is what parse() makes
#
class Document(ENode):
	def __init__(self, root, decl=None):
		ENode.__init__(self, root)
		self.__decl = decl
		self.__root = root
		self.__root._setdocument(self)
	
	def __getitem__(self, key):
		return self.__root[key]
	
	def __len__(self):
		return len(self.__root)
	
	@property
	def nodeType(self):
		return TPythonNode.DOCUMENT_NODE
	
	@property
	def nodeName(self):
		return "#document"
	
	@property
	def childNodes(self):
		return tuple(self.documentElement)
	
	@property
	def documentElement(self):
		return self.__root
	
	@property
	def doctype(self):
		for decl in self.__decl:
			if decl and decl[0].upper() == 'DOCTYPE' and len(decl)>1:
				return decl[1]
		return None
	
	
	def getElementsByTagName(self, tagname, node=None, accum=None):
		r = accum or []
		self.__getelementsbytagname(tagname, node, r)
		return r
	
	def __getelementsbytagname(self, tagname, node, accum):
		# if node's None provided, use root element
		if not node:
			#print ('not node')
			node = self.documentElement
		
		if node.hasChildNodes():
			for n in node.childNodes:
				if n.nodeName == tagname:
					accum.append(n)
				if n.hasChildNodes():
					self.__getelementsbytagname(tagname, n, accum)





#
# ELEMENT - Tags
#
class Element(ENode):
	
	def __init__(self, tag='', attrs=()):
		Node.__init__(self)
		self.__attributes = NamedNodeMap(self) # i'm the parent
		self.__children = NodeList()
		
		nn = tag.split(":")
		self.__nodename = tag
		self.__localname = nn[-1]
		self.__prefix = ":".join(nn[:-1])
		
		for item in attrs:
			if (len(item)>1) and (item[1]!=None):
				self.__attributes[item[0]] = DOMString(item[1])
			else:
				self.__attributes[item[0]] = None
	
	
	def __len__(self):
		return len(self.__children)
	
	def __getitem__(self, item):
		return self.__children[item]
	
	@property
	def nodeType(self):
		return TPythonNode.ELEMENT_NODE
	
	@property
	def nodeName(self):
		return self.__nodename
	
	@property
	def attributes(self):
		return self.__attributes
	
	@property
	def childNodes(self):
		return tuple(self.__children) if self.__children else tuple()
	
	@property
	def firstChild(self):
		try:
			return self.__children[0]
		except IndexError:
			return None
	
	@property
	def lastChild(self):
		try:
			return self.__children[-1]
		except IndexError:
			return None
	
	@property
	def previousSibling(self):
		return self.parentNode._prevchild(self)
	
	@property
	def nextSibling(self):
		return self.parentNode._nextchild(self)
	
	@property
	def localName(self):
		return self.__localname
	
	@property
	def prefix(self):
		return self.__prefix
	
	def hasAttributes(self):
		return True if len(self.attributes) else False
	
	def hasChildNodes(self):
		return True if len(self.__children) else False
	
	def appendChild(self, newChild):
		if newChild.parentNode and (newChild in newChild.parentNode):
			newChild.parentNode.removeChild(newChild)
		newChild._setparent(self)
		self.__children.append(newChild)
	
	def insertBefore(self, newChild, refChild):
		i = self.__children.index(refChild)
		self.__children.insert(newChild, i)
	
	def removeChild(self, oldChild):
		self.__children.remove(oldChild)
		return oldChild
	
	def normalize(self):
		txt = []
		for n in self.children:
			if n.nodeType == NodeType.TEXT:
				txt.append(n.text)
				self.removeChild(t)
			elif txt:
				newText = Text(self, u''.join(txt))
				self.__children.insertBefore(newText, n)
				txt = []
		
		if txt:
			newText = Text(self, u''.join(txt))
			self.__children.appendChild(newText)
	
	def _prevchild(self, n):
		try:
			return self.__children[self.__children.index(n)-1]
		except IndexError:
			return None
	
	def _nextchild(self, n):
		try:
			return self.__children[self.__children.index(n)+1]
		except IndexError:
			return None





#
# ROOT ELEMENT
#  - This is the element with white-space surrounding the html tag.
#    It's the (only) one containeed by the Document object.
#
class RootElement(Element):
	
	# this needs an __init__ to for setting doc (as _setdocumet 
	# currently does. It needs to be passed the Document, anyway,
	# so as to 
	
	def _setdocument(self, doc):
		self.__doc = doc # this is the Document that Parse() makes
	
	@property
	def ownerDocument(self):
		try:
			return self.__doc
		except:
			return None
	
	@property
	def nodeName(self):
		return "/"
	
	@property
	def nextSibling(self):
		return None
	
	@property
	def previousSibling(self):
		return None
	
	



#
# CHARACTER DATA
#
class CharacterData(Node):
	def __init__(self, data):
		Node.__init__(self)
		self.__data = data
	
	def __str__(self):
		return self.__data
	
	def __repr__(self):
		return "<%s:[%s]>" % (self.nodeName, len(self.__data))
	
	@property
	def nodeType(self):
		return TPythonNode.DOCUMENT_NODE
	
	@property
	def nodeName(self):
		return NotImplementedError()
	
	@property
	def nodeValue(self):
		return self.__data
	
	@property
	def length(self):
		return len(self.__data)
	
	@property
	def data(self):
		return self.__data
	
	def substringData(self, offset, count):
		return self.__data[offset:offset+count]
	
	def appendData(self, data):
		self.__data = ''.join([self.__data, data])
	
	def insertData(self, offset, data):
		self.__data = ''.join(
			[self.__data[:offset], data, self.__data[offset:]]
		)
	
	def deleteData(self, offset, count):
		self.__data = ''.join(
			[self.__data[:offset], self.__data[offset+count:]]
		)
	
	def replaceData(self, offset, count, data):
		self.__data = ''.join(
			[self.__data[:offset], data, self.__data[offset+count:]]
		)





#
# COMMENT
#
class Comment (CharacterData):
	
	@property
	def nodeType(self):
		return TPythonNode.COMMENT_NODE
	
	@property
	def nodeName(self):
		return "#comment"
	




#
# TEXT
#
class Text (CharacterData):
	
	@property
	def nodeType(self):
		return TPythonNode.TEXT_NODE
	
	@property
	def nodeName(self):
		return "#text"
	
	def splitText(self, offset):
		raise NotImplementedError() # TODO





#
# CDATA
#
class CDATASection (CharacterData):
	
	@property
	def nodeType(self):
		return TPythonNode.CDATA_SECTION_NODE
	
	@property
	def nodeName(self):
		return "#cdata-section"





#
# PROCESSING INSTRUCTION
#
class ProcessingInstruction (Node):
	def __init__(self, target, data):
		Node.__init__(self)
		self.target = target
		self.data = data
	
	@property
	def nodeType(self):
		return TPythonNode.PROCESSING_INSTRUCTION_NODE
	
	@property
	def nodeName(self):
		return self.target
	
	@property
	def nodeValue(self):
		return self.data





#
# NODE LIST
#
class NodeList(list):
	
	@property
	def length(self):
		return self.len()
	
	def item(self, i):
		return self[i]





#
# NAMED NODE MAP (dom version of a dict)
#
class NamedNodeMap(dict):
	"""
	Implements DOM NamedNodeMap; based on python dict.
	"""
	def __init__(self, parent=None):
		dict.__init__(self)
		self.__parent = parent # not a Node, so save parent!
	
	def getNamedItem(self, name):
		"""Returns the node with the specified name."""
		v = self.get(name)
		return Attr(name, v, self.__parent)
	
	def getNamedItemNS(self, ns, name):
		"""Returns the node with the specific namespace and name."""
		return Attr(name, self.get("%s:%s" % (ns,name)), self.__parent)
		
	def item(self, i):
		"""Returns the node at the specified index."""
		k = self.keys()[i]
		return Attr(k, self.get(k), self.__parent)
	
	def removeNamedItem(self, name):
		"""Removes the node with the specific name"""
		del(self[name])
	
	def removeNamedItemNS(self, ns, name):
		"""Removes the node with the specific name and namespace"""
		del(self["%s:%s" % (ns,name)])
	
	def setNamedItem(self, name, value):
		"""Sets the specified node (by name)"""
		self[name] = DOMString(value)
	
	def setNamedItemNS(self, ns, name, value):
		"""Sets the specified node (by name and namespace)"""
		self["%s:%s" % (ns, name)] = DOMString(value)





#
# ATTRIBUTE
#
class Attr(Node):
	"""A DOM Attribute."""
	
	def __init__(self, name, value, parent=None):
		Node.__init__(self, parent)
		self.__name = name
		self.__value = value
	
	def __str__(self):
		return DOMString(self.value)
	
	def __repr__(self):
		return "%s('%s', '%s')" % (type(self).__name__, self.name, self.value)
	
	@property
	def nodeType(self):
		return TPythonNode.ATTRIBUTE_NODE
	
	@property
	def nodeValue(self):
		return self.__value
	
	@property
	def name(self):
		return self.__name
	
	@property
	def value(self):
		return self.__value
	
	@property
	def specified(self):
		return (self.ownerElement == None) or (self.__value != None)


