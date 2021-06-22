# to be run inside CASA 6.1
import sys, os

sys.path.append(os.getcwd())  # to be able to find check_line
import get_spectrum

image_name = "golden.image.pbcor"
mask_name = "golden.mask"
end_name = "golden"

cube = get_spectrum_CASA.ImageCube(image_name, mask_name, end_name)
cube.get_spectrum(end_name)
