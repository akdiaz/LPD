# to be run inside CASA 6.1
from casatasks import *


class ImageCube:
    """A CASA image with RA, DEC, and frequency axis, with its associated mask."""

    def __init__(self, image_name, mask_name, end_name):
        # check that mask image is not just 0s
        self.image = "cube_" + end_name + ".image"
        self.mask = "cube_" + end_name + ".mask"
        print(">>> Importing cube...")
        importfits(fitsimage=image_name + ".fits", imagename=self.image, overwrite=True)
        print(">>> Importing mask...")
        importfits(fitsimage=mask_name + ".fits", imagename=self.mask, overwrite=True)
        # these images should be deleted later

    def get_spectrum(self, end_name):
        log_file = "spectrum_{}.txt".format(end_name)
        print(">>> Taking spectrum and writing to disk...")
        specflux(
            imagename=self.image,
            mask=self.mask,
            unit="MHz",
            logfile=log_file,
            overwrite=True,
        )
