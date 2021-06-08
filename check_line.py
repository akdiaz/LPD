import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sig

class Spectrum:
    '''This is a spectrum class. Initialises with a text file.'''
    
    def  __init__(self,log_file):
        self.frequency, self.flux = np.loadtxt(log_file, usecols=(2,4), unpack = True)
    
    def potential_lines(self, list_file):
        transition_frequencies = np.loadtxt(list_file, usecols=[1])
        species, transitions = np.loadtxt(list_file, usecols=(0,2),dtype='str', unpack=True)
        f_min = min(self.frequency)
        f_max = max(self.frequency)
        potential_lines=[]
        for index, f in enumerate(transition_frequencies):
            if f_min <= f <= f_max:
                potential_lines.append([species[index], transitions[index], f])
        return potential_lines


    def find_lines(self,separation=50):
        #separation should be in velocity
        rms = np.std(self.flux)
        peaks = sig.find_peaks(self.flux, height=3*rms,distance=separation)
        pos_peaks = peaks[0]
        freq_peaks = [self.frequency[pos] for pos in pos_peaks] 
        flux_peaks = [self.flux[pos] for pos in pos_peaks]
        return rms, freq_peaks, flux_peaks
        
#this is just for reference while I code        
    def make_plot(self,log_file, lines, rms, freq_peaks, flux_peaks):
        fig, ax = plt.subplots()
        ax.plot(self.frequency, self.flux)
        ax.scatter(freq_peaks,flux_peaks,c='r')
        x_lims = ax.get_xlim()
        ax.hlines(rms,x_lims[0],x_lims[1])
        ax.annotate(f'rms = {rms:.2f}',(0.1,rms+rms/10),xycoords=('axes fraction','data'))
        y_lims = ax.get_ylim()
        for l in lines:
          ax.vlines(l[2], y_lims[0], y_lims[1] ,'r')
          ax.annotate(' '.join([l[0],l[1]]),(l[2],0.9),xycoords=('data','axes fraction'))
        fig.savefig(log_file[:-4]+'.png',bbox_inches='tight')
        
        
