import unittest, os

def mode(mode): return unittest.skipUnless(os.environ.get('TESTMODE',default=mode)==mode, f'not a {mode} test')

development = mode('dev')

production = mode('prod')