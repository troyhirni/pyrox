>>> 
>>> 
>>> # THIS IS NOTABLE (See results below)
>>> 
>>> class mTest(object):
...   def test(self, d={}, **k):
...     d.update(k)
...     print(d)
... 
>>> mt = mTest()
>>> mt.test(x=9) # Result 1 is as expected
{'x': 9}
>>> 
>>> mt.test(y=8) # Result 2 may be unexpected
{'y': 8, 'x': 9}
>>> 
>>> 
>>> 
>>> # WORKAROUND - Correct for expected results
>>> 
>>> class nTest(object):
...   def test(self, d=None, **k):
...     d = d or {}
...     d.update(k)
...     print (d)
... 
>>> nt = nTest()
>>> nt.test(x=1)
{'x': 1}
>>> nt.test(y=2)
{'y': 2}
>>> 
>>> 
>>> 
>>> # JUST CHECKING - Results are as expected
>>> 
>>> tt = mTest()
>>> tt.test({'x':1})
{'x': 1}
>>> tt.test({'y':2})
{'y': 2}
>>> 
>>> 
>>> 
>>> 
>>> def test(**k):
...   print k
... 
>>> test(x=1)
{'x': 1}
>>> test(y=2)
{'y': 2}
>>> 
>>> 
>>> 
>>> class Test(object):
...   def test(self, **k):
...     print(k)
... 
>>> t = Test()
>>> t.test(x=1)
{'x': 1}
>>> t.test(x=2)
{'x': 2}
>>> 
>>> 
>>> 
