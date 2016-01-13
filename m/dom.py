"""
Copyright 2016 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

DOM - Under Construction
"""


from xml.dom import Node as TPythonNode





#
# NODE
#  - Every node has a parent; only the root node's is None.
#
class Node(TPythonNode):
	
	def __init__(self, parent):
		self.__id = id(self)
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
		return tupel(*self.__children)
	
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





# -------------------------------------------------------------------
#
# ELEMENT
# -------------------------------------------------------------------
"""
attributes	Returns a NamedNodeMap of attributes for the element
baseURI	Returns the absolute base URI of the element
childNodes	Returns a NodeList of child nodes for the element
firstChild	Returns the first child of the element
lastChild	Returns the last child of the element
localName	Returns the local part of the name of the element
namespaceURI	Returns the namespace URI of the element
nextSibling	Returns the node immediately following the element
nodeName	Returns the name of the node, depending on its type
nodeType	Returns the type of the node
ownerDocument	Returns the root element (document object) for an element
parentNode	Returns the parent node of the element
prefix	Sets or returns the namespace prefix of the element
previousSibling	Returns the node immediately before the element
schemaTypeInfo	Returns the type information associated with the element
tagName	Returns the name of the element
textContent	Sets or returns the text content of the element and its descendants
"""
class Element(Node):
	"""
	The DOM Document object.
	
	Notes:
	 - Elements may have children, siblings
	 - Store offset in parent's children list.
	
	Reference: http://www.w3schools.com/XML/dom_element.asp
	"""
	
	def __init__(self, parent, attrs=None):
		Node.__init__(ELEMENT_NODE, parent, attrs)
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
	
	def _textcontent(self):
		for x in self.childNodes():
			if x.nodeType == Node.TEXT_NODE:
				t.append(x)
		return self.__attrs
	
	@property
	def tagName(self):
		return self.__attrs
	
	def baseURI(self):
		"""Returns the absolute base URI of the element"""
		pass

	def childNodes(self):
		"""Returns a NodeList of child nodes for the element"""
		pass

	def firstChild(self):
		"""Returns the first child of the element"""
		pass

	def lastChild(self):
		"""Returns the last child of the element"""
		pass

	def localName(self):
		"""Returns the local part of the name of the element"""
		pass

	def namespaceURI(self):
		"""Returns the namespace URI of the element"""
		pass

	def nextSibling(self):
		"""Returns the node immediately following the element"""
		pass

	def nodeName(self):
		"""Returns the name of the node, depending on its type"""
		pass



# -------------------------------------------------------------------
#
# DOCUMENT
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
	
	def adoptNode(sourcenode):
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
	
	# MORE TO COME
	


