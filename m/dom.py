"""
Copyright 2016 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

DOM - UNDER CONSTRUCTION

Will provide an XML/HTML parser with partial DOM implementation.
The main goal here is to safely gather data from unknown sources
without being too particular about perfection in their formatting.
We're here for the data.
"""

try:
	from ..base import *
except:
	from base import *

from xml.dom import Node as TPythonNode


DOMString = unicode



# -------------------------------------------------------------------
#
# NODE
#  - CHECK: use parentNode or ownerElement? What's the difference?
#
# -------------------------------------------------------------------
class Node(object):
	def __init__(self, parent):
		self.__parent = parent
	
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
	
	def appendChild(self, newChild):
		pass
	
	def insertBefore(self, newChild, refChild):
		pass
	
	def removeChild(self, oldChild):
		return None
	
	def normalize(self):
		pass



# -------------------------------------------------------------------
#
# NODE LIST
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
# NAMED NODE MAP
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
# ATTR - Attribute Node
#
# -------------------------------------------------------------------
class Attr(Node):
	"""
	A DOM Attribute.
	"""
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
		"""
		I hope this is the correct way to calculate whether an attribute
		is "specified".	I'm not too sure how to interpret this:
		https://www.w3.org/TR/2000/REC-DOM-Level-2-Core-20001113/core.html#ID-862529273
		"""
		return (self.ownerElement == None) or (self.__value != None)



# -------------------------------------------------------------------
#
# ELEMENT
#
# -------------------------------------------------------------------

class Element(Node):
	"""
	Reference: http://www.w3schools.com/XML/dom_element.asp
	"""
	
	def __init__(self, name, attrs=None, parent=None):
		Node.__init__(self, parent)
		self.__document = parent.document if parent else None
		self.__attributes = NamedNodeMap(self) # i'm the parent
		self.__children = []
		
		nn = name.split(":")
		self.__nodename = name
		self.__localname = nn[-1]
		self.__prefix = ":".join(nn[:-1])
		#self.__namespaceuri = None # TODO - maybe someday;
		
		if attrs:
			for item in attrs:
				v = DOMString(item[1]) if len(item)>1 else None
				self.__attributes[item[0]] = item[1] if len(item)>1 else None
	
	
	@property
	def nodeType(self):
		return TPythonNode.ELEMENT_NODE
	
	@property
	def nodeName(self):
		return self.nodename
	
	@property
	def attributes(self):
		return self.__attributes
	
	@property
	def childNodes(self):
		"""
		A list of nodes contained within this node. This is a read-only
		attribute.
		"""
		return tuple(*self.__children) if self.__children else tuple()
	
	@property
	def previousSibling(self):
		"""
		The node that immediately follows this one with the same parent.
		If this is the last child of the parent, this attribute will be 
		None. This is a read-only attribute.
		"""
		return self.parent._prevchild()
	
	@property
	def nextSibling(self):
		"""
		The node that immediately follows this one with the same parent.
		If this is the last child of the parent, this attribute will be 
		None. This is a read-only attribute.
		"""
		return self.parent._nextchild()
	
	@property
	def childNodes(self):
		"""
		A list of nodes contained within this node. This is a read-only
		attribute.
		
		The list is slice [:] of the 
		"""
		return tupel(*self.__children) if self.__children else tupel()
	
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
	def localName(self):
		return self.__localname
	
	@property
	def prefix(self):
		return self.__prefix
	
	@property
	def namespaceURI(self):
		return None #self.__namespaceuri
	
	@property
	def nodeName(self):
		return self.__nodename
	
	def hasAttributes(self):
		return True if len(self.attributes) else False
	
	def hasChildNodes(self):
		return True if len(self.childNodes) else False
	
	def appendChild(self, newChild):
		newChild.parentNode.removeChild(newChild)
		self.__children.append(newChild)
	
	def insertBefore(self, newChild, refChild):
		i = self.__children.index(refChild)
		self.__children.insert(newChild, i)
	
	def removeChild(self, oldChild):
		i = self.__children.remove(oldChild)
		return oldChild
	
	def normalize(self):
		txt = []
		for n in self.children:
			if n.nodeType == NodeType.TEXT:
				txt.append(n.text)
				self.removeChild(t)
			elif txt:
				newText = xText(self, u''.join(txt))
				self.__children.insertBefore(newText, n)
				txt = []
		
		if txt:
			newText = xText(self, u''.join(txt))
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
# DOCUMENT
#
# -------------------------------------------------------------------

class Document(Node):
	"""
	The DOM Document object.
	 - Holds root node
	 * Raise NotImplemented if method is intentionally not implemented.
	 * Raise NotImplememtedError() if a method is on the to-do list.
	
	Reference: http://www.w3schools.com/XML/dom_document.asp
	"""
	def __init__(self):
		Node.__init__(self, None)
	
	def adoptNode(self, sourcenode):
		raise NotImplemented()
	
	@property
	def nodeType(self):
		return TPythonNode.DOCUMENT_NODE
	
	@property
	def nodeName(self):
		return "#document"
	
	@property
	def doctype(self):
		raise NotImplementedError()
	
	@property
	def documentElement(self):
		raise NotImplementedError()
	
	@property
	def documentURI(self):
		raise NotImplementedError()
	
	def createAttribute(self, name):
		"""
		Creates an attribute node with the specified name, and returns 
		the new Attr object
		"""
		pass
	
	def createAttributeNS(self, uri, name):
		"""
		Creates an attribute node with the specified name and namespace,
		and returns the new Attr object
		"""
		pass
	
	def createCDATASection(self, content):
		"""Creates a CDATA section node"""
		pass
	
	def createComment(self, comment):
		"""Creates a comment node"""
		pass
	
	def createDocumentFragment(self):
		"""Creates an empty DocumentFragment object, and returns it"""
		pass
	
	def createElement(self):
		"""Creates an element node"""
		pass
	
	def createElementNS(self):
		"""Creates an element node with a specified namespace"""
		pass
	
	def createEntityReference(self, name):
		"""Creates an EntityReference object, and returns it"""
		pass
	
	def createProcessingInstruction(self, target, data):
		"""Creates a ProcessingInstruction object, and returns it"""
		pass
	
	def createTextNode(self):
		"""Creates a text node"""
		pass
	
	def getElementById(self, id):
		"""
		Returns the element that has an ID attribute with the given 
		value. If no such element exists, it returns null
		"""
		pass
	
	def getElementsByTagName(self):
		"""Returns a NodeList of all elements with a specified name"""
		pass
	
	def getElementsByTagNameNS(self):
		"""
		Returns a NodeList of all elements with a specified name and 
		namespace
		"""
		pass
	
	def importNode(self, nodetoimport, deep):
		"""
		Imports a node from another document to this document. This 
		method creates a new copy of the source node. If the deep 
		parameter is set to true, it imports all children of the 
		specified node. If set to false, it imports only the node 
		itself. This method returns the imported node
		"""
		pass
	
	def normalizeDocument(self):
		pass
		 
	def renameNode(self):
		"""Renames an element or attribute node"""
		pass
	
	