import numpy as np
import matplotlib.pyplot as plt

RMS = 1
X_MIN = 330500
X_MAX = 330674
X_RESOLUTION = 0.1
# gaussian line parameters
GAUSS_PEAK = 10
GAUSS_CENTER = 330587.8671
GAUSS_SIGMA = 2.5


def gaussian(x, a, x0, sigma):
    y = a*np.exp(-(x-x0)**2/(2*sigma**2))
    return y
    
def write_spectrum(x,y):
    header = 'Synthetic spectrum generated for testing\nChannel\tnumber_of_unmasked_pixels\tfrequency_(MHz)\tVelocity_(km/s)\tFlux_density_(Jy)'
    channel = np.arange(x.size)
    zeros = np.zeros(x.size)
    data = np.column_stack((channel, zeros, x, zeros, y))
    fmt = ['%i']*2 + ['%.5f']*3
    np.savetxt('spectrum_golden.txt', data, header=header, fmt=fmt)


#generate data
x = np.arange(X_MIN, X_MAX, X_RESOLUTION)
y = gaussian(x, GAUSS_PEAK, GAUSS_CENTER, GAUSS_SIGMA)
noise = np.random.normal(0,RMS/2,x.size)
y_noise = y+noise

#plot data
fig, ax = plt.subplots()
ax.plot(x,y_noise)
fig.savefig('golden_spectrum_synth.png',bbox_inches='tight')

#save spectrum
write_spectrum(x,y_noise)
