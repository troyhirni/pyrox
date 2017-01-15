"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

MUNGER
configExample = {
	'algo' : [['md5',3188,'Optional-Extra:Salt'], ['sha512',9998]],
	'salt' : 'used-EVERY-iteration-ALL-algos'
}

"""

import random

# RAND (float)
def rand():
	"""Returns a random float."""
	return random.random()

# RAND-I (int)
def randi(size=9):
	"""Returns a random integer."""
	return int(round(rand() * pow(10,size)))

# RAND-IS str(int)
def randis(size=9):
	"""Returns a random integer in string format."""
	return str(randi(size))


def randgen(ct, fn, *a, **k):
	"""
	Pass the number of times `ct` that function (or lambda) `fn` should
	be called. Function `fn` should return a single value of any type.
	Finally, pass any args and/or kwargs to be sent to the function.
	
	CAUTION: if arg `ct` is 0 or None, the generator will go forever.
	"""
	if ct:
		for i in range(0, ct):
			yield fn(*a, **k)
	else:
		while True:
			yield fn(*a, **k)


#
# RANDOM BYTES GENERATOR
#

def bytegen(n=64):
	"""
	Generator for random bytes. Pass the number of bytes you need, or
	(be careful...) pass None for a generator that runs forever.
	"""
	if n:
		for i in range(0,n):
			yield chr(random.randint(0,255))
	else:
		while True:
			yield chr(random.randint(0,255))



# SALT
def salt (size=64, full=True):
	if full:
		return ''.join(randombytes(N))
	return base64.b64encode(os.urandom(N))
