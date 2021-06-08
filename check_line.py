import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sig
from scipy.optimize import curve_fit

WIDTH_LINE = 50 #now is in channels, must be in velocity or frequency = 50
SNR = 3 #signal-to-noise ratio of the peaks to be detected

#probably need to use two gaussians to account for the absorption
def gaussian(x, a, x0, sigma):
    y = a*np.exp(-(x-x0)**2/(2*sigma**2))
    return y

class Spectrum:
    '''This is a spectrum class. Initialises with a text file.'''
    
    def  __init__(self,log_file):
        self.frequency, self.flux = np.loadtxt(log_file, usecols=(2,4), unpack = True)
    
    def potential_lines(self, list_file):
        transition_frequencies = np.loadtxt(list_file, usecols=[1])
        species, transitions = np.loadtxt(list_file, usecols=(0,2),dtype='str', unpack=True)
        minimum = min(self.frequency)
        maximum = max(self.frequency)
        potential_lines=[]
        for index, frequency in enumerate(transition_frequencies):
            if minimum <= frequency <= maximum:
                potential_lines.append([species[index], transitions[index], frequency])
        return potential_lines


    def find_lines(self,separation=WIDTH_LINE):
        #separation is in channels, mind this when changing width_line to velocity
        rms = np.std(self.flux)
        peaks = sig.find_peaks(self.flux, height=SNR*rms,distance=separation)
        position_peaks = peaks[0]
        frequency_peaks = [self.frequency[pos] for pos in position_peaks] 
        flux_peaks = [self.flux[pos] for pos in position_peaks]
        return rms, frequency_peaks, flux_peaks
        
    def get_line_parameters(self, flux_peak, frequency_peak, width=WIDTH_LINE):
        popt, pcov = curve_fit(gaussian, self.frequency, self.flux, p0 = [flux_peak, frequency_peak, width])
        return popt, pcov
        
        
#this is just for reference while I code        
    def make_plot(self,log_file, lines, rms, frequency_peaks, flux_peaks, popt):
        fig, ax = plt.subplots()
        #plot the spectrum
        ax.plot(self.frequency, self.flux, label='data')
        #plot the peaks
        ax.scatter(frequency_peaks,flux_peaks,c='r')
        x_lims = ax.get_xlim()
        ax.hlines(rms,x_lims[0],x_lims[1])
        ax.annotate(f'rms = {rms:.2f}',(0.1,rms+rms/10),xycoords=('axes fraction','data'))
        y_lims = ax.get_ylim()
        for l in lines:
          ax.vlines(l[2], y_lims[0], y_lims[1] ,'r')
          ax.annotate(' '.join([l[0],l[1]]),(l[2],0.9),xycoords=('data','axes fraction'))
        #plot the gaussian fitting
        gaussian_flux = gaussian(self.frequency, *popt)
        ax.plot(self.frequency, gaussian_flux, label='fit')
        ax.legend()
        fig.savefig(log_file[:-4]+'.png',bbox_inches='tight')
        
        
