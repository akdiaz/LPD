import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
import sys

__, vlrs = sys.argv 

RMS = 1
VLRS = float(vlrs) #km/s
FREQUENCY_WINDOW = 100 #MHz
FREQUENCY_RESOLUTION = 0.1
# gaussian line parameters
GAUSS_PEAK = [10]
GAUSS_CENTER = [330587.8671] #in MHz
GAUSS_SIGMA = [2.5]


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
    
    
def write_spectrum(x_freq,x_vel,y):
    header = 'Synthetic spectrum generated for testing\n\n\nChannel\tnumber_of_unmasked_pixels\tfrequency_(MHz)\tVelocity_(km/s)\tFlux_density_(Jy)'
    channel = np.arange(x_freq.size)
    zeros = np.zeros(x_freq.size)
    data = np.column_stack((channel, zeros, x_freq, x_vel, y))
    fmt = ['%i']*2 + ['%.5f']*3
    np.savetxt(f'spectrum_golden_synth_vlrs_{VLRS}.txt', data, header=header, fmt=fmt)

#becouse of Doppler effect
redshifted_freq = redshifted_frequency(GAUSS_CENTER, VLRS)
central_freq = np.mean(redshifted_freq)

#generate data
x_freq = np.arange(central_freq-FREQUENCY_WINDOW/2, central_freq+FREQUENCY_WINDOW/2+FREQUENCY_RESOLUTION, FREQUENCY_RESOLUTION)

y = np.zeros(x_freq.size)
for peak, center, sigma in zip(GAUSS_PEAK, redshifted_freq, GAUSS_SIGMA):
    y = y + gaussian(x_freq, peak, center, sigma)

noise = np.random.normal(0, RMS/2, x_freq.size)
y_noise = y + noise

#find velocity resolution and make velocity column.
'''this implementation is equivalent to make a cube with the rest frequency equal to central_freq. i.e. the central velocity channel will be equal to VLRS'''
x_vel_resolution = -1 * redshifted_frequency(FREQUENCY_RESOLUTION, VLRS)
velocity_window = FREQUENCY_WINDOW * x_vel_resolution/FREQUENCY_RESOLUTION
x_vel = np.linspace(VLRS-velocity_window/2, VLRS+velocity_window/2, x_freq.size)

#plot data
fig, ax = plt.subplots(2,1)
ax[0].plot(x_freq,y_noise)
ax[0].set_xlabel('Frequency (MHz)')
ax[1].plot(x_vel,y_noise)
ax[1].set_xlabel('Velocity (km/s)')
ax[1].invert_xaxis()
y_label = 'Flux (Jy)'
ax[0].set_ylabel(y_label)
ax[1].set_ylabel(y_label)
fig.tight_layout() 
fig.savefig(f'golden_spectrum_synth_vlrs_{VLRS}.png',bbox_inches='tight')

#save spectrum
write_spectrum(x_freq, x_vel, y_noise)
