"""
Copyright 2014-2015 Troy Hirni
This file is part of the aimy project, distributed under
the terms of the GNU Affero General Public License.

AUTH - Simple user authentication.
	
Carp.

"""

from . import hash


SQL = {
	
}



class Auth(Base):
	
	def __init__(self, config=None, **k):
		
		# 
		conf = config if config else {}
		conf.update(k)
		
		self.__hash = hash.Hash(conf['hash'])
		

	