"""
Copyright 2014-2017 Troy Hirni
This file is part of the pyro project, distributed under the terms 
of the GNU Affero General Public License.

DEMO TASK - Add-1

The Add1 demo task waits for dict a message with question 'q', an
integer {'q':8} and replies by adding 1 to generate an answer 
message {'q':8, 'a':9}.

"""


from ..task import *


class Add1(Task):
	def onMessage(self, m):
		if 'q' in m:
			m['a'] = m['q']+1
			self.put(m)
		else:
			Task.onMessage(self, m)

