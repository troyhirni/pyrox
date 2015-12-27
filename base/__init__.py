"""
Copyright 2015 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.
"""


try:
	basestring
except:
	basestring = unicode = str


import json


DEF_ENCODE = 'utf-8'
DEF_INDENT = 2
JSON_INDENT = DEF_INDENT



# EVAL
def jeval(s):
	return json.loads(s)


# J-SMALL
def jsmall(data):
	kw = dict(indent=0, separators=(',',':'), cls=JSONDisplay)
	return ''.join(json.dumps(data, **kw).splitlines())


# J-STRING
def jstring(data, **kwargs):
	"""
	JSON string describing the given data. Kwargs
	are send directly to json.dumps(). (Kwarg defaults
	for 'indent' and 'cls' are set to JSON_INDENT and
	JSONDisplay, respectively.)
	"""
	kwargs.setdefault('indent', JSON_INDENT)
	kwargs.setdefault('cls', JSONDisplay)
	return json.dumps(data, **kwargs)


#
# FAIL-SAFE ENCODER
#
class JSONDisplay(json.JSONEncoder):
	def default(self, obj):
		try:
			return json.JSONEncoder.default(self, obj)
		except TypeError:
			return repr(obj)


