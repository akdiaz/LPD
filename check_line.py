import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sig
from scipy.optimize import curve_fit
from sys import exit

WIDTH_LINE = 50 #in channels
SNR = 3 #signal-to-noise ratio of the peaks to be detected

#probably need to use two gaussians to account for the absorption
def gaussian(x, a, x0, sigma):
    y = a*np.exp(-(x-x0)**2/(2*sigma**2))
    return y

class Spectrum:
    '''This is a spectrum class. Initialises with a text file.'''
    
    def  __init__(self,log_file):
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


    def find_lines(self,separation=WIDTH_LINE):
        print('Finding detected lines in the spectrum...')
        #separation is in channels, mind this when changing width_line to velocity
        rms = np.std(self.flux)
        peaks = sig.find_peaks(self.flux, height=SNR*rms,distance=separation)
        position_peaks = peaks[0]
        frequency_peaks = [self.frequency[pos] for pos in position_peaks] 
        flux_peaks = [self.flux[pos] for pos in position_peaks]
        return rms, frequency_peaks, flux_peaks
        
    def get_line_parameters(self, flux_peak, frequency_peak, width=WIDTH_LINE):
        print('Making Gaussian fits to the lines...')
        popt = []
        pcov = []
        for flux, frequency in zip(flux_peak,frequency_peak):
            popt_temporal, pcov_temporal = curve_fit(gaussian, self.frequency, self.flux, p0 = [flux, frequency, width])
            popt.append(popt_temporal)
            pcov.append(pcov_temporal)
        return popt, pcov
        
    def match_lines(self, potential_lines, popt, tolerance):
        potential_frequency = np.array([pot_line[2] for pot_line in potential_lines])
        frequency_founded_lines = np.array([parameter[1] for parameter in popt])
        actual_lines=[]
        for frequency in frequency_founded_lines:
            distance = potential_frequency-frequency
            index_minimum = np.argmin(distance)
            if abs(distance[index_minimum]) < tolerance:
                actual_lines.append(potential_lines[index_minimum])
            else:
                actual_lines.append(['U','U','0'])
        return actual_lines
       
    def write_parameters(self, actual_lines, popt, pcov):
        print('Writing output file...')
        errors = [np.sqrt(matrix.diagonal()) for matrix in pcov]
        #need to add the unit, make the convertion from sigma to HPBW, and add velocities
        header = 'Species\tTransition\tFrequency\tRedshifted_Frequency\tError\tFlux\tError\tSigma\tError'        
        molecules = np.array([i[0] for i in actual_lines]) 
        transitions = np.array([i[1] for i in actual_lines])
        frequencies = np.array([i[2] for i in actual_lines])
        flux = np.array([i[0] for i in popt]) 
        redshifted_frequencies = np.array([i[1] for i in popt])
        sigma = np.array([i[2] for i in popt])
        flux_error = np.array([i[0] for i in errors]) 
        redshifted_frequencies_error = np.array([i[1] for i in errors])
        sigma_error = np.array([i[2] for i in errors])
        #format of columns in data
        columns_dtype = [('molecule', 'U25'), ('transition', 'U25'), ('frequency', float), ('redshifted_frequency', float), ('redshifted_frequency_error', float), ('flux', float), ('flux_error', float), ('sigma', float), ('sigma_error', float)]
        fmt = ['%s']*2+['%f']*7
        #write data
        data = np.zeros(molecules.size, dtype=columns_dtype)
        data['molecule'] = molecules
        data['transition'] = transitions
        data['frequency'] = frequencies
        data['redshifted_frequency'] = redshifted_frequencies
        data['redshifted_frequency_error'] = redshifted_frequencies_error
        data['flux'] = flux
        data['flux_error'] = flux_error
        data['sigma'] = sigma
        data['sigma_error'] = sigma_error
        np.savetxt('detected_lines.txt', data, header=header, fmt=fmt)
        
#this is just for reference while I code        
    def make_plot(self,log_file, lines, rms, frequency_peaks, flux_peaks, popt):
        print('Making plot...')
        fig, ax = plt.subplots()
        #plot the spectrum
        ax.plot(self.frequency, self.flux, label='data')
        #plot the peaks
        ax.scatter(frequency_peaks,flux_peaks,c='r')
        x_lims = ax.get_xlim()
        ax.hlines(rms,x_lims[0],x_lims[1])
        ax.annotate(f'rms = {rms:.2f}',(x_lims[0],rms+rms/10),xycoords='data')
        #plot the potential lines
        y_lims = ax.get_ylim()
        for l, fitted_parameters in zip(lines, popt):
            if l[0] == 'U':
                ax.vlines(fitted_parameters[1], y_lims[0], y_lims[1] ,'r')
                ax.annotate(' '.join([l[0],l[1]]),(fitted_parameters[1],0.9),xycoords=('data','axes fraction'))   
            else:
                ax.vlines(l[2], y_lims[0], y_lims[1] ,'r')
                ax.annotate(' '.join([l[0],l[1]]),(l[2],0.9),xycoords=('data','axes fraction'))
        #plot the gaussian fitting
        for index, fitted_parameters in enumerate(popt):
            gaussian_flux = gaussian(self.frequency, *fitted_parameters)
            ax.plot(self.frequency, gaussian_flux, label='fit_'+str(index))
        ax.legend()
        fig.savefig(log_file[:-4]+'.png',bbox_inches='tight')
        
        
