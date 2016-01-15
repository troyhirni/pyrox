"""
Copyright 2016 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

DOM - Under Construction

REFERENCES:
http://www.w3schools.com/XML/dom_nodetype.asp


"""


from xml.dom import Node as TPythonNode





#
# NODE
#  - Every node has a parent; only the root node's is None.
#
class Node(TPythonNode):
	
	def __init__(self, document, parent):
		self.__document = document
		self.__nodeid = id(self)
		self.__parent = parent 
		self.__children = []
		
		# ----------- TO DO -------------
		self.__localname = None
		self.__prefix = None
		self.__namespaceuri = None
		self.__nodename = None
	
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
	
	@property
	def ownerDocument(self):
		"""Returns the root element (document object) for a node."""
		return self.__document
	
	@property
	def nodeType(self):
		"""
		An integer representing the node type. Symbolic constants for 
		the types are on the Node object: ELEMENT_NODE, ATTRIBUTE_NODE,
		TEXT_NODE, CDATA_SECTION_NODE, PROCESSING_INSTRUCTION_NODE,
		COMMENT_NODE, DOCUMENT_NODE, ENTITY_NODE,	DOCUMENT_TYPE_NODE,
		NOTATION_NODE. This is a read-only attribute.
		"""
		return None # SUBCLASSES RETURN A VALID ENTITY_CODE
	
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
	def attributes(self):
		return None # Element returns self.__attributes
	
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
		return self.__namespaceuri
	
	@property
	def nodeName(self):
		return self.__nodename
	
	@property
	def nodeValue(self):
		raise NotImplemented()
	
	def hasAttributes(self):
		return True if len(self.attributes) else False
	
	def hasChildNodes(self):
		return True if len(self.childNodes) else False
	
	def isSameNode(self, other):
		return self.__nodeid == other.__nodeid
	
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
	
	
	# 
	# .........   YOU    ARE    HERE   .........
	#
	def cloneNode(self, deep):
		pass

	def isDefaultNamespace(self, URI):
		"""Returns whether the specified namespaceURI is the default"""
		pass

	def isEqualNode(self):
		"""Tests whether two nodes are equal"""
		pass

	def lookupNamespaceURI(self):
		"""Returns the namespace URI associated with a given prefix"""
		pass

	def lookupPrefix(self):
		"""Returns the prefix associated with a given namespace URI"""
		pass

	def getFeature(self, feature, version):
		"""
		Returns a DOM object which implements the specialized APIs of 
		the specified feature and version
		"""
		pass
		
	def getUserData(self, key):
		"""
		Returns the object associated to a key on a this node. The 
		object must first have been set to this node by calling 
		setUserData with the same key
		"""
		pass



# -------------------------------------------------------------------
#
# ELEMENT
#
# -------------------------------------------------------------------

class Element(Node):
	"""
	The DOM Document object.
	
	Notes:
	 - Elements may have children, siblings
	 - Store offset in parent's children list.
	
	Reference: http://www.w3schools.com/XML/dom_element.asp
	"""
	
	def __init__(self, document, parent, attrs=None):
		Node.__init__(self, document, parent, attrs)
		self.__attrs = attrs or []
	
	@property
	def nodeType(self):
		return Node.ELEMENT_NODE
	
	@property
	def attributes(self):
		return self.__attrs
	
	@property
	def textContent(self):
		t = []
		for x in self.childNodes():
			if x.nodeType == Node.TEXT_NODE:
				t.append(x)
			else:
				txt = x.textContent
				if txt:
					t.append('')
		return t
	
	@property
	def tagName(self):
		return self.__attrs
	
	def baseURI(self):
		"""Returns the absolute base URI of the element"""
		pass
	
	def localName(self):
		"""Returns the local part of the name of the element"""
		pass
	
	def namespaceURI(self):
		"""Returns the namespace URI of the element"""
		pass
	
	def nodeName(self):
		"""Returns the name of the node, depending on its type"""
		pass

	def schemaTypeInfo(self):
		"""Returns the type information associated with the element"""
		pass



# -------------------------------------------------------------------
#
# NAMED NODE MAP
#
# -------------------------------------------------------------------
class NamedNodeMap(Node):
	
	def __init__(self, attrs=None):
		self.__ns = {}
		self.__items = {}
	
	def getNamedItem(self, name):
		"""Returns the node with the specific name"""
		return self.get(name)
	
	def getNamedItemNS(self, name):
		"""Returns the node with the specific name and namespace"""
		
	def item(self, i):
		"""Returns the node at the specified index"""
		pass
	
	def removeNamedItem(self, name):
		"""Removes the node with the specific name"""
		pass
	
	def removeNamedItemNS(self, name, ns):
		"""Removes the node with the specific name and namespace"""
		pass
	
	def setNamedItem(self, name):
		"""Sets the specified node (by name)"""
		pass
	
	def setNamedItemNS(self, name, ns):
		"""Sets the specified node (by name and namespace)"""
		pass
	




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
		return Node.DOCUMENT_NODE
	
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
	
	