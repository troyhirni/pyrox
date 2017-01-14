
try:
	from ._io import Opener
except:
	try:
		from ._codecs import Opener
	except:
		try:
			from ._open import Opener
		except:
			from ._file import Opener
