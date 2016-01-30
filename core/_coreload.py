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

# core
try:
	from .. import core
except:
	import core

reload(core)
