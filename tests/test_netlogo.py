"""
Created on 23 mrt. 2013

@author: localadmin
"""
import unittest

try:
    import unittest.mock as mock
except ImportError:
    import mock

import src.pynetlogo as pynetlogo


class Test(unittest.TestCase):
    @mock.patch("src.pynetlogo.core.os")
    def test_find_netlogo(self, mocked_os):
        mocked_os.path.abspath.return_value = "/Applications"
        mocked_os.listdir.return_value = [
            "Netlogo 6.1",
            "Netlogo 6.2",
            "Netlogo 6.3",
        ]

        version = pynetlogo.core.find_netlogo("/Applications")
        self.assertEqual(version, "Netlogo 6.3")

        mocked_os.listdir.return_value = ["Netlogo 6.1", "Netlogo 6.2"]

        version = pynetlogo.core.find_netlogo("/Applications")
        self.assertEqual(version, "Netlogo 6.2")

        mocked_os.listdir.return_value = []
        with self.assertRaises(IndexError):
            pynetlogo.core.find_netlogo("/Applications")

    def testNetlogoLink(self):
        pass
        #         link = pynetlogo.NetLogoLink(True, False)
        #         link = pynetlogo.NetLogoLink(True, True)
        #         link = pynetlogo.NetLogoLink(False, False)
        #         link = pynetlogo.NetLogoLink(False, True)
        pass

    #     def test_load_model(self):
    #         link = netlogo.NetLogo(True, False)
    #         link.load_model(netlogo.NETLOGO_HOME + r'/models/Sample Models/Biology/Wolf Sheep Predation.nlogo')

    def test_command(self):
        pass

    def test_report(self):
        pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
