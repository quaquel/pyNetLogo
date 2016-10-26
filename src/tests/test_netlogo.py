'''
Created on 23 mrt. 2013

@author: localadmin
'''
from __future__ import (absolute_import, unicode_literals, print_function, 
                        division)

import unittest
try:
    import unittest.mock as mock
except ImportError:
    import mock
import pyNetLogo.pyNetLogo as pyNetLogo
 
class Test(unittest.TestCase):
 
    @mock.patch('pyNetLogo.pyNetLogo.os')
    def test_find_netlogo(self, mocked_os):
        mocked_os.path.abspath.return_value = '/Applications'
        mocked_os.listdir.return_value = ['Netlogo 5.1.1', 'Netlogo 5.3.0',
                                          'Netlogo 6.0']
        
        version = pyNetLogo.find_netlogo('/Applications')
        self.assertEqual(version, 'Netlogo 6.0')
        
        
        mocked_os.listdir.return_value = ['Netlogo 5.1.1', 'Netlogo 5.3']
        
        version = pyNetLogo.find_netlogo('/Applications')
        self.assertEqual(version, 'Netlogo 5.3')
        
        mocked_os.listdir.return_value = []
        with self.assertRaises(IndexError):
            pyNetLogo.find_netlogo('/Applications')
        
        
    def testNetlogoLink(self):
        pass
#         link = pyNetLogo.NetLogoLink(True, False)
#         link = pyNetLogo.NetLogoLink(True, True)
#         link = pyNetLogo.NetLogoLink(False, False)
#         link = pyNetLogo.NetLogoLink(False, True)
        pass
     
#     def test_load_model(self):
#         link = netlogo.NetLogo(True, False)
#         link.load_model(netlogo.NETLOGO_HOME + r'/models/Sample Models/Biology/Wolf Sheep Predation.nlogo')
     
    def test_command(self):
        pass
     
    def test_report(self):
        pass
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()