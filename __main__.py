"""
Copyright 2016 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

Prompt for an object specified by package.module.class; additional
arguments are passed to constructor.

EXAMPLE: python pyrox base.fs.Dir ./pyrox/base
"""

import sys

if __name__ == '__main__':
	
	app = sys.argv[0]
	cmd = sys.argv[1] if len(sys.argv) > 1 else ''
	args = sys.argv[2:]
	
	if not cmd or (cmd in ['-h', '--help']):
		print ("\nUSAGE: python %s [[package.]module.]class" % (app))
	elif cmd == '--clean':
		from base import fs
		d = fs.Dir()
		d.find('.', '*.pyc', fn=d.rm)
	else:
		import base
		from base import prompt
		try:
			obj = base.Factory(cmd).create(*args)
		except TypeError:
			pe = cmd.split('.')
			obj = __import__(cmd, globals(), locals(), pe[:-1])
		prompt.prompt(obj)
	
