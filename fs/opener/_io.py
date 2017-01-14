"""
Copyright 2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.
"""

import io

class Opener(object):
	def open(self, *a, **k):
		return io.open(*a, **k)

