import sys, os
sys.path.append(os.getcwd()) #to be able to find check_line
import check_line

image_name = 'golden.image.pbcor'
mask_name = 'golden.mask'
end_name = 'golden'

cube  = check_line.ImageCube(image_name, mask_name, end_name)
spect = cube.get_spectrum(end_name)
