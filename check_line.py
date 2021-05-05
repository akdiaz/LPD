#to be run inside CASA
import numpy as np

class image_cube:
	'''This is a image_cube class. It is a CASA image with RA, DEC, and frequency axis.'''
	
	def __init__(self, image_name, mask_name, end_name):
		self.image = 'cube_'+end_name+'.image'
		self.mask = 'cube_'+end_name+'.mask'
		importfits(fitsimage=image_name+'.fits',imagename=self.image)
		importfits(fitsimage=mask_name+'.fits',imagename=self.mask)

	def make_spectrum(self,log_name):
		specflux(imagename=self.image, mask=self.mask, unit='MHz',logfile=log_name)

class spectrum:
	'''This is a spectrum class. Initialises with a text file.'''
	
	def  __init__(self,log_name):
		ch, n_pix, freq, vel, flux = np.loadtxt(log_name, unpack = True)
		self.channel = ch
		self.frequency = freq
		self.velocity = vel
		self.flux_density = flux


image_name = 'member.uid___A001_X133d_X3abb.HOPS-007_sci.spw3.cube.I.manual.image.pbcor'
mask_name = 'member.uid___A001_X133d_X3abb.HOPS-007_sci.spw3.cube.I.manual.mask'
end_name = 'spw3'
log_name='spectrum_'+end_name+'.txt'

cube  =  image_cube(image_name, mask_name, end_name)
cube.make_spectrum(log_name)

spect = spectrum(log_name)
