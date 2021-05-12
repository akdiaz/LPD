#to be run inside CASA 6.1
import numpy as np
import tempfile
import matplotlib.pyplot as plt
from casatasks import *

class ImageCube:
    '''A CASA image with RA, DEC, and frequency axis, with its associated mask.'''
    
    def __init__(self, image_name, mask_name, end_name):
        #check that mask image is not just 0s
        self.image = 'cube_'+end_name+'.image'
        self.mask = 'cube_'+end_name+'.mask'
        importfits(fitsimage=image_name+'.fits',imagename=self.image, overwrite=True)
        importfits(fitsimage=mask_name+'.fits',imagename=self.mask, overwrite=True)
        #these images should be deleted later
        #do I want to keep the spectrum?
        

    def get_spectrum(self,end_name):
        with tempfile.NamedTemporaryFile(delete=False, suffix='_{}.txt'.format(end_name)) as fd:
            log_file = fd.name
        specflux(imagename=self.image, mask=self.mask, unit='MHz',logfile=log_file, overwrite=True)
        return Spectrum(log_file)

class Spectrum:
    '''This is a spectrum class. Initialises with a text file.'''
    
    def  __init__(self,log_file):
        self.frequency, self.flux = np.loadtxt(log_file, usecols=(2,4), unpack = True)
    
    #this doesn't work with my instalation of CASA 6.1
    def make_plot(self):
        fig, ax = plt.subplots()
        ax.plot(self.frequency, self.flux)
        fig.savefig(log_file[:-4]+'.png',bbox_inches='tight')

    def potential_lines(self, list_file):
        transition_frequencies = np.loadtxt(list_file, usecols=1)
        species, transitions = np.loadtxt(list_file, usecols=(0,2),dtype='str', unpack=True)
        f_min = min(self.frequency)
        f_max = max(self.frequency)
        potential_lines=[]
        for index, f in enumerate(transition_frequencies):
            if f_min <= f <= f_max:
                potential_lines.append([species[index], transitions[index], f])
        return potential_lines


