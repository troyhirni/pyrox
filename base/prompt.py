"""
Copyright 2014-2015 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

Prompt - Interact with python objects as though in a shell.
"""

try:
	from ..base import *
except:
	from base import *

from . import fmt


import time


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
		self.__f = k.get('format', None)
	
	@property
	def dir(self):
		return dir(self.__o)
	
	@property
	def dict(self):
		return self.__o.__dict__
	
	# INPUT
	def input(self, p=None):
		try:
			return textinput(p if p else self.__p)
		except EOFError:
			time.sleep(1) # relief for win8+/py2 interpreter bug
	
	# OUTPUT
	def output(self, x):
		print(self.__f(x) if self.__f else x)
	
	# PARSE (command line)
	def parse(self, s):
		return s.lstrip().split()
	
	# PROMPT
	def prompt(self, **k):
		o = self.__o if self.__o else self
		p = k.get('prompt', self.__p)
		m = k.get('guide', self.__m)
		r = None
		if m:
			print (m)
		try:
			while True:
				s = self.input(p)
				r = None
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
			return r
	
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


