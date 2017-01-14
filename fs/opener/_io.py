
import io

class Opener(object):
	def open(self, *a, **k):
		return io.open(*a, **k)

