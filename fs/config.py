"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

CONFIG - Read/Write config files

"""


import ast, json
from . import *
from ..fmt import JSONDisplay


class Config(Path):
	
	def __init__(self, path, **k):
		Path.__init__(self, path)
		self.__k = k
	
	
	def write(self, data, **k):
		"""Write data to this object's file path as JSON."""
		k.setdefault('cls', JSONDisplay)
		k.setdefault('indent', DEF_INDENT)
		k.setdefault('encoding', DEF_ENCODE)
		self.writer("w").write(unicode(json.dumps(data, **self.__k)))
	
	
	def read(self):
		"""Read config from this object's file path."""
		txt = self.reader("r", **self.__k).read()
		try:
			try:
				return ast.literal_eval(txt)
			except:
				compile(txt, self.path, 'eval') #try to get a line number
				raise
		except BaseException as ast_ex:
			try:
				return json.loads(txt)
			except BaseException as json_ex:
				raise Exception ("config-read-error", xdict(
					path = self.path, pathk = k,
					ast = {"type" : type(ast_ex), "args" : ast_ex.args},
					json = {"type" : type(json_ex), "args" : json_ex.args}
				))



