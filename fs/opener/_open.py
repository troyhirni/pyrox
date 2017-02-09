"""
Copyright 2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

OPEN OPENER - Uses the built-in `open` method.

This may appear at first glance to be unnecessary, but it's 
definitely needed if only so that the right keyword arguments can be
filtered before the call. Later versions of python will use io.open
or codecs.open, with more kwargs available to those methods.
"""

from .. import *


class Opener(object):
	def open(self, *a, **k):
		kk = Base.kcopy(k, "mode buffering")
		try:
			return open(*a, **k)
		except Exception as ex:
			raise type(ex)('open-fail', xdata(a=a, k=k, opener=Opener))

