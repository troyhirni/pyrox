"""
Copyright 2015-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

IMPORTER - Unicode Data Importer  -  DEMO! -  UNDER CONSTRUCTION!!!

I'm including this in case anyone wants to play around with it. I'll
try to smooth it out as time goes by.

ADJUST VARIABLES  BEFORE RUNNING THIS SCRIPT! (You may also need to
move this file outside the udata subpackage before running it.)

There are still a lot of imporvements to make, obviously, but it does
replace the python files in ucdpy with a fresh copy created from the
data in a UCD.zip file.

UCD.zip can be downloaded from here:
http://www.unicode.org/Public/UCD/latest/ucd/UCD.zip
"""

#
# ADJUST THIS! Change the path to whereever you've placed UCD.zip
#
UCD_ZIP_FILE = '~/dev/data/unicode/9.0.0/UCD.zip'

#
# ADJUST THIS! Change this path to point to your ucdpy subpackage
#
PX_UCDPY_DIR = '~/dev/pyrox/udata/ucdpy'


#from pyrox.data import pdq
from pyrox.fs import zip, dir

# This is the path on my system to the UCD.zip file
udb = zip.Zip(UCD_ZIP_FILE)

# The directory in which I want the result files written
out = dir.Dir(PX_UCDPY_DIR, affirm='makedirs')



#
# --- PROP-LIST ----------------------------------------------------
#
r = udb.reader(member='PropList.txt', encoding='utf-8')
d = {}
for line in r:
	l = line.strip()
	if l and (l[0] != '#'):
		row = line.split('#')
		pair = row[0].strip().split(';')
		key = pair[1].strip()
		value = pair[0].strip().split('..')
		if len(value)==1:
			value = "0x%s" % value[0]
		elif len(value)==2:
			value = "[0x%s, 0x%s]" % (value[0],value[1])
		else:
			raise Exception('invalid line: PropList.txt file')
		
		if key in d:
			d[key].append(value)
		else:
			d[key] = [value]


# output
dest = out('proplist.py').wrapper()
w = dest.writer(encoding='utf8')
w.write(u"""
#
# PropList
#

""")

quiet = w.write(u"\nPROPERTIES = {")
comma = ''
for key in d:
	
	quiet = w.write (u"%s\n\t'%s' : [%s]" % (
		comma, key, ", ".join(d[key])
	))
	comma = ','

quiet = w.write (u"\n}\n")
w.close()






#
# --- BLOCKS -------------------------------------------------------
#
r = udb.reader(member='Blocks.txt', encoding='utf-8')
rr = []
for line in r:
	l = line.strip()
	if l and (l[0] != '#'):
		row = line.split(';')
		value = row[0].strip().split('..')
		block = row[1].strip()
		rr.append([value, block])

# strip internal values
for x in rr:
	x[0][0] = x[0][0].strip()
	if len(x[0])>1:
		x[0][1] = x[0][1].strip()


# output
dest = out('blocks.py').wrapper()
w = dest.writer(encoding='utf8')
w.write(u"""
#
# Blocks
#

""")

quiet = w.write(u"\nBLOCKS = [\n")
comma = ''
for row in rr:
	value = row[0]
	quiet = w.write (u"%s\n\t[[0x%s, 0x%s], '%s']" % (
		comma, value[0], value[1], row[1]
	))
	comma = u','

quiet = w.write (u"\n]\n")
w.close()




#
# --- BIDI BRACKETS ------------------------------------------------
#
r = udb.reader(member='BidiBrackets.txt', encoding='utf-8')
rr = []
for line in r:
	l = line.strip()
	if l and (l[0] != '#'):
		row = line.split('#')
		bidi = row[0].strip().split(';')
		comment = row[1].strip()
		rr.append([bidi, comment])

# strip internal values
for x in rr:
	x[0][1] = x[0][1].strip()
	x[0][2] = x[0][2].strip()


# output
dest = out('bidi.py').wrapper()
w = dest.writer(encoding='utf8')
w.write(u"""
#
# BidiBrackets
#

""")

w.write(u"\nBRACKETPAIRS = [\n")
c = ''
for r in rr:
	b = r[0]
	w.write (u"%s\n\t[0x%s, 0x%s, '%s'], # %s" % (
		c, b[0], b[1], b[2], r[1]
	))
	c = ','

quiet = w.write (u"\n]\n")
w.close()

