import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u

RMS = 1
VLRS = 8 #km/s 
FREQ_WINDOW = 100 #MHz
X_RESOLUTION = 0.1
# gaussian line parameters
GAUSS_PEAK = 10
GAUSS_CENTER = 330587.8671 #in MHz
GAUSS_SIGMA = 2.5


def gaussian(x, a, x0, sigma):
    y = a*np.exp(-(x-x0)**2/(2*sigma**2))
    return y

def redshifted_frequency(f, vlrs):
    ''' Assumes (for now) rest frequency (f) in MHz and velocity of the source (vlrs) in km/s.'''
    f_rest = f*u.MHz #rest frequency
    vlrs = vlrs*u.km/u.s # velocity of the source
    relativistic_equiv = u.doppler_relativistic(f_rest)
    f_shifted = vlrs.to(u.MHz, equivalencies=relativistic_equiv)
    return f_shifted.value    
    
    
def write_spectrum(x,y):
    header = 'Synthetic spectrum generated for testing\nChannel\tnumber_of_unmasked_pixels\tfrequency_(MHz)\tVelocity_(km/s)\tFlux_density_(Jy)'
    channel = np.arange(x.size)
    zeros = np.zeros(x.size)
    data = np.column_stack((channel, zeros, x, zeros, y))
    fmt = ['%i']*2 + ['%.5f']*3
    np.savetxt('spectrum_golden.txt', data, header=header, fmt=fmt)

#becouse of Doppler effect
redshifted_freq = redshifted_frequency(GAUSS_CENTER, VLRS)

#generate data
x = np.arange(redshifted_freq-FREQ_WINDOW/2, redshifted_freq+FREQ_WINDOW/2, X_RESOLUTION)
y = gaussian(x, GAUSS_PEAK, redshifted_freq, GAUSS_SIGMA)
noise = np.random.normal(0,RMS/2,x.size)
y_noise = y+noise

#plot data
fig, ax = plt.subplots()
ax.plot(x,y_noise)
fig.savefig('golden_spectrum_synth.png',bbox_inches='tight')

#save spectrum
write_spectrum(x,y_noise)
