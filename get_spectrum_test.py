import unittest
import sys, os

sys.path.append(os.getcwd())  # to be able to find check_line
import get_spectrum
import numpy as np
import shutil

TEST_DATA_PATH = "tests/data"
BASE_NAME = "golden"


class SpectrumTest(unittest.TestCase):
    def test_mask_all_zero(self):
        """Make sure that you can tell if a mask is all zeros."""
        mask_all_zero = os.path.join(TEST_DATA_PATH, "casa_images", "zeros.mask")
        is_zero = get_spectrum.is_mask_all_zero(mask_all_zero)
        self.assertEqual(is_zero, True)

    def test_import_fits(self):
        """Make sure that the fits images are imported correctly into CASA"""

        name = os.path.join(TEST_DATA_PATH, "fits", BASE_NAME)
        image_path = name + ".image"
        mask_path = name + ".mask"

        if os.path.isdir(image_path):
            shutil.rmtree(image_path)
        if os.path.isdir(image_path):
            shutil.rmtree(image_path)

        get_spectrum.ImageCube(name)

        self.assertEqual(os.path.isdir(image_path), True)
        self.assertEqual(os.path.isdir(mask_path), True)

    def test_take_spectrum(self):
        """Make sure that the spectrum is taken correctly."""

        true_spectrum = os.path.join(TEST_DATA_PATH, BASE_NAME) + ".spectrum.true.txt"

        cube = get_spectrum.ImageCube(BASE_NAME)
        spectrum = cube.get_spectrum()
        frequency_golden, flux_golden = np.loadtxt(
            true_spectrum, usecols=(2, 4), unpack=True
        )
        frequency, flux = np.loadtxt(
            BASE_NAME + ".spectrum.txt", usecols=(2, 4), unpack=True
        )
        self.assertListEqual(list(frequency), list(frequency_golden))
        self.assertListEqual(list(flux), list(flux_golden))


unittest.main(exit=False, verbosity=2)
