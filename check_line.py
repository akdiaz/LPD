import numpy as np
import matplotlib.pyplot as plt

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

    def make_plot(self,log_file,lines):
        fig, ax = plt.subplots()
        ax.plot(self.frequency, self.flux)
        y_lims = ax.get_ylim()
        for l in lines:
          ax.vlines(l[2], y_lims[0], y_lims[1] ,'r')
          ax.annotate(' '.join([l[0],l[1]]),(l[2],0.9),xycoords=('data','axes fraction'))
        fig.savefig(log_file[:-4]+'.png',bbox_inches='tight')
