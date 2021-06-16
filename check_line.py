import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sig
from scipy.optimize import curve_fit
from sys import exit
from functools import lru_cache

def gaussian(x, a, x0, sigma):
    y = a*np.exp(-(x-x0)**2/(2*sigma**2))
    return y
    
def match_lines(potential_lines, detected_lines_frequency, tolerance):
    potential_frequency = np.array([pot_line[2] for pot_line in potential_lines])
    actual_lines=[]
    for frequency in detected_lines_frequency:
        distance = potential_frequency-frequency
        index_minimum = np.argmin(distance)
        if abs(distance[index_minimum]) < tolerance:
            actual_lines.append(potential_lines[index_minimum])
        else:
            actual_lines.append(['U','U','0'])
    return actual_lines
    
      
class Spectrum:
    '''This is a spectrum class. Initialises with a text file.'''
    
    def  __init__(self,log_file):
        self.columns = np.loadtxt(log_file, skiprows=3, max_rows=1, comments=None, dtype='str', usecols=(3,4,5))
        self.frequency, self.velocity, self.flux = np.loadtxt(log_file, usecols=(2,3,4), unpack = True)
        self.frequency_resolution = self.frequency[1]-self.frequency[0]
        self.velocity_resolution = self.velocity[1]-self.velocity[0]        
    
    def potential_lines(self, list_file):
        print('Finding expected lines in the spectrum...')
        transition_frequencies = np.loadtxt(list_file, usecols=[1])
        species, transitions = np.loadtxt(list_file, usecols=(0,2),dtype='str', unpack=True)
        minimum = min(self.frequency)
        maximum = max(self.frequency)
        potential_lines=[]
        for index, frequency in enumerate(transition_frequencies):
            if minimum <= frequency <= maximum:
                potential_lines.append([species[index], transitions[index], frequency])
        if len(potential_lines) == 0:
            exit('There is no potential lines in the frequency range of the spectrum. Edit the file <<lines.txt>>.')
        return potential_lines

    @property
    @lru_cache(10)
    def rms(self):
        print('Finding rms of the spectrum...')
        values, edges = np.histogram(self.flux, bins=100)
        popt, _ = curve_fit(gaussian, edges[:-1], values, p0 = [max(self.flux), 0, 1])
        return abs(popt[-1])

    def find_lines(self, snr, width):
        print('Finding detected lines in the spectrum...')
        #separation is in channels, mind this when changing width_line to velocity
        peaks = sig.find_peaks(self.flux, height=snr*self.rms, distance=width)
        position_peaks = peaks[0]
        return self.frequency[position_peaks], self.velocity[position_peaks], self.flux[position_peaks]
        
    def write_parameters(self, actual_lines, peak_frequency, peak_velocity, peak_flux):
        print('Writing output file...')
        header = 'Species\tTransition\tFrequency\t'+f'Peak_{self.columns[0]}\tPeak_{self.columns[1]}\tPeak_{self.columns[2]}'
        molecules = np.array([i[0] for i in actual_lines]) 
        transitions = np.array([i[1] for i in actual_lines])
        frequencies = np.array([i[2] for i in actual_lines])
        #format of columns in data
        columns_dtype = [('molecule', 'U25'), ('transition', 'U25'), ('frequency', float), ('peak_frequency', float), ('peak_velocity', float), ('peak_flux', float)]
        fmt = ['%s']*2+['%f']*4
        #write data
        data = np.zeros(molecules.size, dtype=columns_dtype)
        data['molecule'] = molecules
        data['transition'] = transitions
        data['frequency'] = frequencies
        data['peak_frequency'] = peak_frequency
        data['peak_velocity'] = peak_velocity
        data['peak_flux'] = peak_flux
        np.savetxt('detected_lines.txt', data, header=header, fmt=fmt)
       
    #this is just for reference while I code        
    def make_plot(self, log_file, lines, frequency_peaks, flux_peaks):
        print('Making plot...')
        fig, ax = plt.subplots()
        #plot the spectrum
        ax.plot(self.frequency, self.flux, label='data')
        #plot the peaks
        ax.scatter(frequency_peaks,flux_peaks,c='r')
        x_lims = ax.get_xlim()
        ax.hlines(self.rms, x_lims[0],x_lims[1])
        ax.annotate(f'rms = {self.rms:.2f}',(x_lims[0],self.rms+self.rms/10),xycoords='data')
        #plot the potential lines
        y_lims = ax.get_ylim()
        for l, freq_peak in zip(lines, frequency_peaks):
            if l[0] == 'U':
                ax.vlines(freq_peak, y_lims[0], y_lims[1] ,'r')
                ax.annotate(' '.join([l[0],l[1]]),(freq_peak, 0.9),xycoords=('data','axes fraction'))   
            else:
                ax.vlines(l[2], y_lims[0], y_lims[1] ,'r')
                ax.annotate(' '.join([l[0],l[1]]),(l[2],0.9),xycoords=('data','axes fraction'))
        ax.legend()
        fig.savefig(log_file[:-4]+'.png',bbox_inches='tight')
