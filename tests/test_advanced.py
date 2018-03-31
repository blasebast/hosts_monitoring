# -*- coding: utf-8 -*-

import unittest
from hmon import read_hosts

class AdvancedTestSuite(unittest.TestCase):
    """Advanced test cases."""

    def test_something(self):
        self.assertTrue(read_hosts("hosts"))

if __name__ == '__main__':
    unittest.main()
