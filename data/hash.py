"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

HASH - Hashing utility

configExample = {
	'algo' : [['md5',3188,'Optional-Extra:Salt'], ['sha512',9998]],
	'salt' : 'used-EVERY-iteration-ALL-algos'
}
"""

from .. import *
import rand

import hashlib

	

class Hash(object):
	
	def __init__(self, config=None, **k):
		"""
		Create a Hash object. Config contains keys "algo" and "salt".
		Value "algo" is a list of lists, each containing 2 to 3 values:
		  * the algo name for hashing (required)
		  * the number of repetitions (required)
		  * salt to apply to the value when hashing (optional)
		
		Optional kwarg guarantee=True forces config's algo list to be in
		the list of hashlib.algorithms_guaranteed, or an Exception is
		raised. If any specified algo is not available, an Exception is
		raised.
		"""
		
		# config
		conf = config or {}
		conf.update(k)
		
		# algo is required
		self.__algo = conf['algo']
		
		# check availability
		chk = list(set([a[0] for a in self.__algo]))
		fail = []
		reason = None
		if k.get('guarantee'):
			clist = hashlib.algorithms_guaranteed
			for a in chk:
				if a not in clist:
					fail.append(a)
			if fail:
				reason = 'algo-not-guaranteed'
		else:
			clist = hashlib.algorithms_available
			for a in chk:
				if a not in clist:
					fail.append(a)
			if fail:
				reason = 'algo-not-available'
		
		# if fail, raise exception
		if reason:
			raise Exception('hash-create-fail', 
				xdata(reason=reason, algo=fail)
			)
	
	
	def hash(self, value, salt=''):
		"""
		Hash the given value with the given salt using algos as specified
		in constructor's config. If given, argument salt is prepended to
		configuration salt for each config-specified algo; any resulting
		salt-combo is appended for each hash update.
		"""
		salt = str(salt)
		for a in self.__algo:
			h = hashlib.new(a[0])
			s = "%s%s"%(salt,(str(a[2]))) if len(a)>2 else salt
			for i in range(0, a[1]):
				h.update('%s%s' % (value, s))
		return h.hexdigest()
	
	
	@classmethod
	def salt(cls, n=64):
		return str(''.join(rand.bytegen(n)))





