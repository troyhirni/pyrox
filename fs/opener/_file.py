
class Opener(object):
	def open(self, *a, **k):
		return file(*a, **k)

