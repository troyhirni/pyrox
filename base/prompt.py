"""
Copyright 2014-2015 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

Prompt - Interact with python objects as though in a shell.

import pyrox as px
d = px.dir()
px.prompt(d)
"""


import time

try:
	_pq_input = raw_input
except:
	_pq_input = input

from .. import base


DEF_PROMPT = '> '
DEF_GUIDE = "Ctrl-c to exit."


#
# PROMPT
#
class Prompt(object):
	
	def __init__(self, o=None, **k):
		self.__o = o if o else self
		self.__p = k.get('prompt', DEF_PROMPT)
		self.__m = k.get('guide', DEF_GUIDE)
		self.__f = k.get('format')
	
	@property
	def dir(self):
		return dir(self.__o)
	
	@property
	def dict(self):
		return self.__o.__dict__
	
	# INPUT
	def input(self, p=None):
		try:
			return _pq_input(p if p else self.__p)
		except EOFError:
			time.sleep(1)
	
	# OUTPUT
	def output(self, x):
		if self.__f is 'json':
			print(base.jstring(x))
		else:
			print (x)
	
	# PARSE (command line)
	def parse(self, s):
		return s.lstrip().split()
	
	# PROMPT
	def prompt(self, **k):
		o = self.__o if self.__o else self
		p = k.get('prompt', self.__p)
		m = k.get('guide', self.__m)
		if m:
			print (m)
		try:
			while True:
				r = None
				s = self.input(p)
				if s.strip():
					line = self.parse(s)
					args = line[1:]
					cmd = line[0]
					try:
						m = getattr(o, cmd)
						r = m(*args)
					except TypeError:
						r = m
					except Exception as ex:
						print (str(ex))
				if r != None:
					self.output (r) 
		except KeyboardInterrupt:
			print()
	
	# TEXT
	def text(self, **k):
		a = []
		p = k.get('prompt', DEF_PROMPT)
		m = k.get('guide', DEF_GUIDE)
		if m:
			print (m)
		try:
			while True:
				a.append(input(p))
		except KeyboardInterrupt:
			pass
		return a


