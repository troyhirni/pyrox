"""
Copyright 2015-2016 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

BASE - Defintions needed by many modules in this package. Expect 
       many changes here during early experimental development. In
       the end, it will consist of most basic needs.
"""

import os


try:
	basestring
	textinput = raw_input

except:
	from imp import reload
	basestring = unicode = str
	unichr = chr
	textinput = input


DEF_ENCODE = 'utf-8'
DEF_INDENT = 2



def expandpath(path=None, **k):
	"""
	Returns an absolute path.
	
	Keyword 'affirm' lets you assign (or restrict) actions to be
	taken if the given path does not exist. 
	 * checkpath - default; raise if parent path does not exist.
	 * checkdir - raise if full given path does not exist.
	 * makepath - create parent path as directory if none exists.
	 * makedirs - create full path as directory if none exists.
	 * touch - create a file at the given path if none exists.
	
	To ignore all validation, pass affirm=None.
	"""
	OP = os.path
	if path in [None, '.']:
		path = os.getcwd()
	
	if not OP.isabs(path): # absolute
		path = OP.expanduser(path)
		if OP.exists(OP.dirname(path)): # cwd
			path = OP.abspath(path)
		else:
			path = OP.abspath(OP.normpath(path))
	
	v = k.get('affirm', "checkpath")
	if (v=='checkpath') and (not OP.exists(OP.dirname(path))):
		raise Exception('no-such-path', {'path' : path})
	if v and (not OP.exists(path)):
		if (v=='checkdir'):
			raise Exception('no-such-dir', {'path' : path})
		elif v in ['makepath', 'touch']:
			if not OP.exists(OP.dirname(path)):
				os.makedirs(OP.dirname(path))
			if v == 'touch':
				with open(path, 'a'):
					os.utime(path, None)
		elif (v=='makedirs'):
			os.makedirs(path)
	
	return path

