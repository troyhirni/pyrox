"""
Copyright 2015 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.
"""

from .base import fs, text, url
from .base import prompt as prompt_

#
# TEST FUNCTIONS
#

def dir(*a, **k):
	return fs.Dir(*a, **k)

def file(*a, **k):
	return fs.File(*a, **k)

def text(*a, **k):
	return text.text(*a, **k)

def url(*a, **k):
	return url.open(*a, **k)


# PROMPT
def prompt(*a, **k):
	p = prompt_.Prompt(*a, **k)
	return p.prompt()
