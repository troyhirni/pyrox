"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under the terms 
of the GNU Affero General Public License.

** MAIN **

python -m pyrox --help
python -m pyrox --ipath # print the `innerpath` to pyrox package
python -m pyrox --test  # test loading of modules and file wrapper io
python -m pyrox --clean # remove .pyc files and __pycache__ directories
"""


import sys
from . import *

if __name__ == '__main__':
	
	app = sys.argv[0]
	cmd = sys.argv[1] if len(sys.argv) > 1 else ''
	args = sys.argv[2:]
	
	# help/how-to reminders
	if not cmd or (cmd in ['-h', '--help']):
		print (__doc__)
	
	# print the arguments received by this call
	elif cmd == '--args':
		print (str(sys.argv))
	
	# print the inner-path for python imports within the package
	elif cmd == '--ipath':
		print ("%s" % (Base.innerpath(*args)))
	
	# test loading of modules and file wrapper io
	elif cmd == '--test':
		from pyrox.dev import test
		test.report()
	
	# remove *.pyc files
	elif cmd == '--clean':
		d = Base.ncreate('fs.dir.Dir', *args[1:])
		d.search('pyrox', '__pycache__', fn=d.rm)
		d.search('pyrox', '*.pyc', fn=d.rm)
	
	
	#
	# ADDITIONAL, FOR FUN
	#
	
	# prompt demo - ftp
	elif cmd == '--ftp':
		print (args)
		d = Base.create('ftplib.FTP', *args)
		p = Base.ncreate('intf.prompt.Prompt', d)
		p.prompt()
	
	# prompt demo - *
	elif cmd == '--prompt':
		d = Base.ncreate(args[0], *args[1:])
		p = Base.ncreate('intf.prompt.Prompt', d)
		p.prompt()

