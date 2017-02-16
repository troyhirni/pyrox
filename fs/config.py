"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

CONFIG - Read/Write config files

"""


import ast, json
from .file import *
from ..fmt import JSONDisplay


class Config(File):
	"""
	Json config files.
	"""
	
	def __init__(self, path, **k):
		
		# EXPERIMENTAL:
		# I'm thinking it may be best to apply a default encoding here;
		# Config files are kind of an internal matter; Whatever default
		# is set to is almost certainly what people will want. We'll see
		# how it goes. For now I'll label this matter "EXPERIMENTAL".
		k.setdefault('encoding', DEF_INDENT)
		File.__init__(self, path, **k)
	
	
	# WRITE
	def write(self, data, **k):
		"""Write config data to this object's file path as JSON."""
		k.setdefault('cls', JSONDisplay)
		k.setdefault('indent', DEF_INDENT)
		
		# json doesn't like encoding-related kwargs
		ek = self.extractEncoding(k)
		
		# write the data
		File.write(self, json.dumps(data, **k), **ek)
	
	
	# READ
	def read(self):
		"""Read config from this object's file path."""
		txt = self.reader().read()
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



