# to be run:
# python3 check_line_test.py

import os
import sys
import unittest

from memoir import check_line


class LinesTest(unittest.TestCase):
    def test_redshifted(self):
        """Make sure that the frequency is correctly refshifted"""
        frequency = 345795.98990  # MHz
        vlsr = 1.0  # km/s
        redshifted_frequency = check_line.redshift_frequency(frequency, vlsr)
        self.assertAlmostEqual(redshifted_frequency, 345794.8364506588, places=5)

    def test_match_lines(self):
        """Make sure that the lines are correctly matched"""
        potential_lines = [
            ["13COv=0", "J=3-2,F=5/2-5/2", 330587.8671, 330587.8671],
            ["13COv=0", "J=3-2,F=7/2-5/2", 330587.9816, 330587.98160],
        ]
        detected_lines_frequency = [330587.8671, 330588.8671]
        tolerance = 0.01
        actual_lines = check_line.match_lines(
            potential_lines, detected_lines_frequency, tolerance
        )
        expected_output = [
            [0, "13COv=0", "J=3-2,F=5/2-5/2", 330587.8671, 330587.8671],
            [1, "U", "U", "0", "0"],
        ]
        self.assertEqual(actual_lines, expected_output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
