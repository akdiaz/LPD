import sys, os
sys.path.append(os.getcwd()) #to be able to find check_line
import check_line

image_name = 'member.uid___A001_X133d_X3abb.HOPS-007_sci.spw3.cube.I.manual.image.pbcor'
mask_name = 'member.uid___A001_X133d_X3abb.HOPS-007_sci.spw3.cube.I.manual.mask'
end_name = 'spw3'
#log_name='spectrum_'+end_name+'.txt'

cube  = check_line.ImageCube(image_name, mask_name, end_name)
spect = cube.get_spectrum(end_name)
