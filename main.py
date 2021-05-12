import sys, os
sys.path.append(os.getcwd()) #to be able to find check_line
import check_line

#image_name = 'golden.image.pbcor'
#mask_name = 'golden.mask'
#end_name = 'golden'

#cube  = check_line.ImageCube(image_name, mask_name, end_name)
#spect = cube.get_spectrum(end_name)

spectrum_name='spectrum_spw0.txt'
list_file='lines.txt'
spect = check_line.Spectrum(spectrum_name)
lines = spect.potential_lines(list_file)
