"""
Copyright 2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

FILE OPENER

I'm not sure this will ever be used, but there's no harm in placing
it here just in case. Only when running the earliest versions of 
python would this be necessary.

"""

class Opener(object):
	def open(self, *a, **k):
		kk = Base.kcopy(k, "mode buffering")
		try:
			return file(*a, **k)
		except Exception as ex:
			raise type(ex)('open-fail', xdata(a=a, k=k, opener=Opener))

