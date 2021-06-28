# to be run inside CASA 6.1
from casatasks import *

def is_mask_all_zero(mask):
        mask_statistics = imstat(
            imagename = mask)
        maximum_value = mask_statistics['max'][0]
        return maximum_value == 0

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

    def get_spectrum(self):
        log_file = f"{self.name}.spectrum.txt"
        print("\t>>> Taking spectrum and writing to disk...")
        if not is_mask_all_zero(self.mask):
            specflux(
                imagename=self.image,
                mask=self.mask,
                unit="MHz",
                logfile=log_file,
                overwrite=True
            )
        else:
            print('\t>>> This mask is all zeros. Moving on...')

    
