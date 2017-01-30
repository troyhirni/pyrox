"""
Copyright 2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

OPEN OPENER - Uses the built-in `open` method.

Used only for earlier versions of python.
"""

from .. import *


class Opener(object):
	def open(self, *a, **k):
		kk = Base.kcopy(k, "mode buffering")
		return open(*a, **k)

