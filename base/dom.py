"""
Copyright 2016 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

DOM   **   UNDER CONSTRUCTION   **   STILL A LONG WAY TO GO.

Will provide an XML/HTML parser with partial DOM implementation.
The main goal here is to safely gather data from unknown sources
without being too particular about perfection in their formatting.
We're here for the data.
"""

try:
	from html.parser import HTMLParser
except:
	from HTMLParser import HTMLParser

try:
	from pyrox.base import *
except:
	from base import *

from xml.dom import Node as TPythonNode



DOMString = unicode




def parse(html):
	p = Parse(unicode(html))
	return Document(p.doc, p.decl) 



#
#
#
# PARSER
#
#
#

class Parse(HTMLParser):
	
	def __init__(self, htmlstr=None):
		HTMLParser.__init__(self)
		
		self.doc = None
		self._decl = [] # DocType plus other declarations
		self._head = [] # before first element; (spaces, comments, etc.)
		
		# these are None until the first element is reached
		self._root = None
		self._acum = None # accumulate nodes inside unclosed elements
		
		# after root closes, elem becomes tail
		self._tail = []
		
		# if string was provided, parse it
		if htmlstr:
			self.feed(htmlstr)
	
	
	
	def handle_starttag(self, tag, attrs):
		try:
			# Append unclosed nodes to a list. They become children of an
			# element once that element is closed (or parsing ends).
			self._acum.append(Element(tag, attrs))
		except:
			self._root = Element(tag, attrs)
			self._acum = [self._root]
			self.doc = Document(self._root, self._decl)
	
	
	
	def handle_startendtag(self, tag, attrs):
		self.handle_starttag(tag, attrs)
	
	
	
	def handle_endtag(self, tag):
		
		# search backward through _acum list
		r = []
		try:
			# pop to the last doc.node matching 'tag'
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
		
		
	#
	# Callbacks that add nodes either to the head (at the beginning
	# of the doc before the first element) or to the current element.
	#
	def _addnode(self, node):
		try:
			# elem is the most recently opened element
			self._acum.append(node)
		except:
			# ..before the first element, append nodes to head.
			self._head.append(node)
	
	def handle_comment(self, data):
		self._addnode(Comment(data))
	
	def handle_data(self, data):
		self._addnode(Text(data))

	def handle_pi(self, data):
		target, data = data.split(None,1)
		self._addnode(ProcessingInstruction(target, data))
	
	def unknown_decl(self, data):
		if data.find("CDATA[") == 0:
			self._addnode(CDATASection(data[6:]))
		else:
			self._addnode(Comment("UNKNOWN DECL: %s" % data))
	
	#
	# DocType
	#
	def handle_decl(self, decl):
		self.decl.append(decl.split(None, 1))





# ---------------------------------------------------------------
#
# DOCUMENT TREE
# Node.__init__
#
# ---------------------------------------------------------------

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
		"""
		The parent of the current node, or None for the document node. 
		The value is always a Node object or None. For Element nodes, 
		this will be the parent element, except for the root element, in 
		which case it will be the Document object. For Attr nodes, this 
		is always None. This is a read-only attribute.
		"""
		return self.__parent
	
	@property
	def ownerElement(self):
		return self.__parent
	
	@property
	def ownerDocument(self):
		"""Returns the root element (document object) for a node."""
		try:
			return self.__document
		except:
			p = self.ownerElement()
			if not p:
				self.__document = self if isinstance(self, DocumentNode) else None
			else:
				self.__document = p.ownerDocument()
			return self.__document
	
	def isSameNode(self, other):
		return id(self) == id(other)
	
	# False None Pass
	@property
	def nodeValue(self):
		return None

	def hasAttributes(self):
		return False
	
	def hasChildNodes(self):
		return False








class Document(Node):
	def __init__(self, root, decl):
		self.__root = root
		self.__decl = decl
	
	def __getitem__(self, key):
		return self.__root[key]
	
	def __len__(self):
		return len(self.__doc)
	
	@property
	def nodeType(self):
		return TPythonNode.DOCUMENT_NODE
	
	@property
	def nodeName(self):
		return "#document"
	
	@property
	def documentElement(self):
		return self.__root







class Element(Node):
	
	def __init__(self, tag=None, attrs=None, d=[]):
		Node.__init__(self)
		self.__attributes = NamedNodeMap(self) # i'm the parent
		self.__children = NodeList()
		
		nn = tag.split(":")
		self.__nodename = tag
		self.__localname = nn[-1]
		self.__prefix = ":".join(nn[:-1])
		
		if attrs:
			for item in attrs:
				if (len(item)>1) and (item[1]!=None):
					self.__attributes[item[0]] = DOMString(item[1])
				else:
					self.__attributes[item[0]] = None
	
	
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
		"""
		A list of nodes contained within this node. This is a read-only
		attribute.
		"""
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
		return self.parent._prevchild()
	
	@property
	def nextSibling(self):
		return self.parent._nextchild()
	
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







# -------------------------------------------------------------------
#
#
#
# CHARACTER DATA, TEXT, COMMENT
#
#
#
# -------------------------------------------------------------------

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







class Comment (CharacterData):
	
	@property
	def nodeType(self):
		return TPythonNode.COMMENT_NODE
	
	@property
	def nodeName(self):
		return "#comment"
	






class Text (CharacterData):
	
	@property
	def nodeType(self):
		return TPythonNode.TEXT_NODE
	
	@property
	def nodeName(self):
		return "#text"
	
	def splitText(self, offset):
		raise NotImplementedError() # TODO







class CDATASection (CharacterData):
	
	@property
	def nodeType(self):
		return TPythonNode.CDATA_SECTION_NODE
	
	@property
	def nodeName(self):
		return "#cdata-section"







class ProcessingInstruction (Node):
	def __init__(target, data):
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







# -------------------------------------------------------------------
#
#
# NODE LIST
#
#
# -------------------------------------------------------------------
class NodeList(list):
	
	@property
	def length(self):
		return self.len()
	
	def item(self, i):
		return self[i]



# -------------------------------------------------------------------
#
#
# NAMED NODE MAP
#
#
# -------------------------------------------------------------------
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



# -------------------------------------------------------------------
#
#
# ATTR - Attribute Node
#
#
# -------------------------------------------------------------------
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
