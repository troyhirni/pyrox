"""
Copyright 2016 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

Reload base package and all base modules.
"""

try:
	reload
except:
	from imp import reload

# base
try:
	from .. import base
except:
	import base

# depend on base
from . import database, dom, fmt, fs, pdq, prompt, text, udata

# depend on modules that depend on base
from . import url, scan

# RELOAD UTIL
reload(base)
reload(database)
reload(dom)
reload(fmt)
reload(fs)
reload(pdq)
reload(prompt)
reload(text)
reload(udata)
reload(url)
reload(scan)
