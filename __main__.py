
import sys
from . import *

if __name__ == '__main__':
	
	app = sys.argv[0]
	cmd = sys.argv[1] if len(sys.argv) > 1 else ''
	args = sys.argv[2:]
	
	# help/how-to reminders
	if not cmd or (cmd in ['-h', '--help']):
		print ("USAGE: python -m %s --clean [path]" % app)
	
	# print the arguments received by this call
	elif cmd == '--args':
		print (str(sys.argv))
	
	# print the arguments received by this call
	elif cmd == '--ipath':
		print ("%s" % (Base.innerpath(*args)))
	
	# remove *.pyc files
	elif cmd == '--clean':
		d = Base.ncreate('fs.dir.Dir', *args[1:])
		d.search('.', '*.pyc', fn=d.rm)
	
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

