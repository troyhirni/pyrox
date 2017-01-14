
import codecs

class Opener(object):
	def open(self, *a, **k):
		return codecs.open(*a, **k)

