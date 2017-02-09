"""
Copyright 2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

CODECS OPENER

"""

from .. import Base
import codecs


class Opener(object):
	def open(self, *a, **k):
		kk = Base.kcopy(k, "mode buffering encoding errors buffering")
		try:
			return codecs.open(*a, **kk)
		except Exception as ex:
			raise type(ex)('open-fail', xdata(a=a, k=k, opener=Opener))

