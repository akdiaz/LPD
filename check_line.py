#to be run inside CASA
import numpy as np
import tempfile
from casatasks import *

class ImageCube:
    '''A CASA image with RA, DEC, and frequency axis, with its associated mask.'''
    
    def __init__(self, image_name, mask_name, end_name):
        self.image = 'cube_'+end_name+'.image'
        self.mask = 'cube_'+end_name+'.mask'
        importfits(fitsimage=image_name+'.fits',imagename=self.image, overwrite=True)
        importfits(fitsimage=mask_name+'.fits',imagename=self.mask, overwrite=True)
        #these images should be deleted later

    def get_spectrum(self,end_name):
        with tempfile.NamedTemporaryFile(delete=False, suffix='_{}.log'.format(end_name)) as fd:
            log_file = fd.name
        specflux(imagename=self.image, mask=self.mask, unit='MHz',logfile=log_file, overwrite=True)
        return Spectrum(log_file)

class Spectrum:
    '''This is a spectrum class. Initialises with a text file.'''
    
    def  __init__(self,log_file):
        ch, _, freq, vel, flux = np.loadtxt(log_file, unpack = True)
        self.channel = ch
        self.frequency = freq
        self.velocity = vel
        self.flux_density = flux
    
    #def make_plot


#image_name = 'member.uid___A001_X133d_X3abb.HOPS-007_sci.spw3.cube.I.manual.image.pbcor'
#mask_name = 'member.uid___A001_X133d_X3abb.HOPS-007_sci.spw3.cube.I.manual.mask'
#end_name = 'spw3'
#log_name='spectrum_'+end_name+'.txt'

#check that mask image is not just 0s

#cube  = ImageCube(image_name, mask_name, end_name)
#spect = cube.get_spectrum(log_name)
