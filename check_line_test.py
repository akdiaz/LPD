import unittest
import sys, os

sys.path.append(os.getcwd())  # to be able to find check_line
import check_line
import numpy as np

TEST_DATA_PATH = "tests/data"

IMAGE_NAME = "golden.image.pbcor"
MASK_NAME = "golden.mask"
END_NAME = "test"
GOLDEN_SPECTRUM = "spectrum_golden.txt"

image_path = os.path.join(TEST_DATA_PATH, IMAGE_NAME)
mask_path = os.path.join(TEST_DATA_PATH, MASK_NAME)
golden_spectrum_path = os.path.join(TEST_DATA_PATH, GOLDEN_SPECTRUM)


class SpectrumTest(unittest.TestCase):
    def test_take_spectrum(self):
        """Make sure that the spectrum is taken correctly."""
        cube = check_line.ImageCube(image_path, mask_path, END_NAME)
        spectrum = cube.get_spectrum(END_NAME)
        frequency_golden, flux_golden = np.loadtxt(
            golden_spectrum_path, usecols=(2, 4), unpack=True
        )
        self.assertListEqual(list(spectrum.frequency), list(frequency_golden))
        self.assertListEqual(list(spectrum.flux), list(flux_golden))


unittest.main(exit=False, verbosity=2)
