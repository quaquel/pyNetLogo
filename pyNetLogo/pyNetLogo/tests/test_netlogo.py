'''
Created on 23 mrt. 2013

@author: localadmin
'''
import unittest
import netlogo

class Test(unittest.TestCase):


    def testNetlogoLink(self):
#        link = netlogo.NetLogo(True, False)
#        link = netlogo.NetLogo(True, True)
#        link = netlogo.NetLogo(False, False)
#        link = netlogo.NetLogo(False, True)
        pass
    
    def test_load_model(self):
        link = netlogo.NetLogo(True, False)
        link.load_model(netlogo.NETLOGO_HOME + r'\models\Sample Models\Biology\Wolf Sheep Predation.nlogo')
    
    def test_command(self):
        pass
    
    def test_report(self):
        pass
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()