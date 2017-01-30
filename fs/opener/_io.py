"""
Copyright 2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

IO OPENER

Used when io.open() is available.
"""

from .. import *
import io

class Opener(object):
	def open(self, *a, **k):
		kk = Base.kcopy(
			k, "mode buffering encoding errors newline closefd"
		)
		return io.open(*a, **kk)

