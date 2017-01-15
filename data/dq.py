"""
Copyright 2015 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

DATA-QUERY - DEMO

The function in this module may be merged into another module.
"""

from .. import xdata


#
# DATA QUERY
#
def dq(dd, query, *args):
	"""
	Follow a path through a dict or list and return a value.
	- The dd argument is a dict or list.
	- The query arg is an array listing each step. It can also be a 
	  string in the form of a file path*, eg '/dogs/shepherds/german'.
	- Examples:
	  >>> dd = {'A':{'b':[9,8,7]}}
	  >>> dq(dd, ['A'])    # {'b':[9,8,7]}
	  >>> dq(dd, '/A/b/1') # 8
	  >>> dq(dd, '/a')     # None (no 'a' key).
	
	* In fact, you can substitute the / with any single character. The 
	  first character of the string is used to split the rest of the 
	  string into a list. For example:
	  >>> dq(dd,'.A.b.2') # 7
	  >>> dq(dd,'xAxbx1') # 8
	  >>> dq(dd,' A b 0') # 9
	"""
	try:
		path = []
		if isinstance(query, str) and query:
			query = query[1:].split(query[0])
		for aa in iter(query):
			path.append(aa)
			if isinstance(dd, dict):
				if aa in dd.keys():
					dd = dd[aa]
				else:
					raise KeyError(path)
			else:
				aa = int(aa)
				if aa < len(dd):
					dd = dd[aa]
				else:
					raise IndexError(path)
		return dd
	except Exception as e:
		raise type(e)('data-query-err', xdata({
			"python" : str(e),
			"path" : path
		}))
	
	default = args[0] if len(args) else None
	if default and callable(default):
		return default()
	return default

