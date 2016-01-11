"""
Copyright 2015 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

BASE - Defintions needed by many modules in this package. Expect 
			 many changes here during early experimental development. In
			 the end, it will consist of most basic needs.
"""

import struct


try:
	basestring
	textinput = raw_input
	

except:
	from imp import reload
	basestring = unicode = str
	textinput = input
	
	def unichr(i):
		return struct.pack('i', i).decode('utf-32') 



DEF_ENCODE = 'utf-8'
DEF_INDENT = 2
