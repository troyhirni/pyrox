"""
Copyright 2015 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.
"""


try:
	basestring
	pxinput = raw_input
except:
	basestring = unicode = str
	pxinput = input


DEF_ENCODE = 'utf-8'
DEF_INDENT = 2


