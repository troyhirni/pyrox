"""
Copyright 2016-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

BZIP - Covers bzip2 files.





"""

from .file import *
import bz2


class Bzip(File):
	"""bzip2 file support."""
	def open(self, mode='r', **k):
		return bz2.BZ2File(self.path, mode, **k)



