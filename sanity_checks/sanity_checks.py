import matplotlib.pyplot as plt
import numpy as np

step = 0 # compares the spectrum made with the script (specflux) with an spectrum made manually with the viewer

if step == 0:
	freq_v, flux_v = np.loadtxt('spectrum_viewer.txt', unpack = True)
	ch, n_pix, freq, vel, flux = np.loadtxt('spectrum.txt', unpack = True)
	
	fig, ax  = plt.subplots()
	ax.plot(freq, flux,'b',label='from script')
	ax.plot(freq_v, flux_v,'r',label='from viewer')
	ax.legend()
	fig.savefig('spectrum.png',bbox_inches='tight')
