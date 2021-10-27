# to be run inside CASA 6.1
from casatasks import *


def is_mask_all_zero(mask):
    mask_statistics = imstat(imagename=mask)
    maximum_value = mask_statistics["max"][0]
    return maximum_value == 0


class ImageCube:
    """A CASA image with RA, DEC, and frequency axis, with its associated mask."""

    def __init__(self, base_name):
        self.name = base_name.replace(".", "_").replace(
            "-", "_"
        )  # because I cannot use masks with several '.' or '-' in the name
        self.image = self.name + ".image"
        self.mask = self.name + ".mask"
        print("\t>>> Importing cube...")
        importfits(
            fitsimage=base_name + ".pbcor.fits",
            imagename=self.image,
            overwrite=True,
        )
        print("\t>>> Importing mask...")
        importfits(
            fitsimage=base_name + ".mask.fits", imagename=self.mask, overwrite=True
        )
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
                overwrite=True,
            )
        else:
            print("\t>>> This mask is all zeros. Moving on...")
