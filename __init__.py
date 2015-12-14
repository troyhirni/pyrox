"""
Copyright 2015 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.
"""

from .base import fs
from .base import prompt as prompt_

# fs
def path(*a, **k):
	return fs.Path(*a, **k)

def file(*a, **k):
	return fs.File(*a, **k)

def dir(*a, **k):
	return fs.Dir(*a, **k)

def prompt(*a, **k):
	p = prompt_.Prompt(*a, **k)
	return p.prompt()

