"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

CSV - File and Reader for CSV

The CSV class is basically just a File class with a different reader.
All other methods are the same, but the reader returns each row as a
list instead of text. I'm not sure what to do when the genrator goes
dead. Currently it just returns None, but I think it needs an EOF.
"""


from .file import *

class CSV(File):
	def reader(self, mode='r', *a, **k):
		return CSVReader(self.open(mode='r'), *a, **k)


class CSVReader(Stream):
	
	def read(self, *a, **k):
		return [r for r in self.readline(*a, **k)]
	
	def readline(self, *a, **k):
		for line in iter(self.linegen(*a, **k)):
			return line
	
	def linegen(self, *a, **k):
		csvr = Base.create('csv.reader', self.stream, *a, **k)
		for line in csvr:
			yield line
	
	