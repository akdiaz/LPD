# to be run:
# python3 check_line_test.py 

import unittest
import sys, os

sys.path.append(os.getcwd())  # to be able to find check_line
import check_line



class LinesTest(unittest.TestCase):
    def test_redshifted(self):
        """Make sure that the frequency is correctly refshifted"""
        frequency = 345795.98990 #MHz
        vlsr = 1.0  #km/s
        redshifted_frequency = check_line.redshift_frequency(frequency, vlsr)
        self.assertEqual(redshifted_frequency, 345794.8364506588)




if __name__ == "__main__":
    unittest.main( verbosity=2)
