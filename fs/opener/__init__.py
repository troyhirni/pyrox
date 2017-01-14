"""
Copyright 2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

OPENER - Opening files

Chooses the most recently available method for opening files. For 
python 2.7 and later, this means the io module's open function. For
earlier versions, the codecs module or python's built-in open() 
function or file() constructor may be used.
"""

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
