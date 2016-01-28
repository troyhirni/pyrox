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
		print ("\nUSAGE: python %s package.module.class" % (app))
	else:
		from base import prompt, factory
		obj = factory.Factory(cmd).create(*args)
		prompt.prompt(obj)
	
