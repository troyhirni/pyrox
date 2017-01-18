"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyro project, distributed under
the terms of the GNU Affero General Public License.

Reload base package and all base modules.
"""

try:
	reload
except:
	from imp import reload

# core
try:
	from .. import core
except:
	import core

reload(core)
