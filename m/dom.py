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
		
		# find document element by going up through parents
		d = dd = parent
		while d:
			dd = d
			d = d.ownerElement
	
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
		return self.__document



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
		"""
		Returns the node with the specific name.
		"""
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
	
	def __init__(self, name, attrs, parent=None):
		Node.__init__(self, parent)
		self.__document = parent.document if parent else None
		self.__attributes = NamedNodeMap(self) # i'm the parent
		self.__children = []
		
		nn = name.split(":")
		self.__nodename = name
		self.__localname = nn[-1]
		self.__prefix = ":".join([:-1])
		#self.__namespaceuri = None # TODO - maybe someday;
		
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
	
	
