import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sig
from scipy.optimize import curve_fit
from sys import exit
from functools import lru_cache
import astropy.units as u
import os


def gaussian(x, a, x0, sigma):
    y = a * np.exp(-((x - x0) ** 2) / (2 * sigma ** 2))
    return y


def redshift_frequency(f, vlsr):
    """Assumes (for now) rest frequency (f) in MHz and velocity of the source (vlsr) in km/s."""
    f_rest = f * u.MHz  # rest frequency
    vlsr = vlsr * u.km / u.s  # velocity of the source
    relativistic_equiv = u.doppler_relativistic(f_rest)
    f_shifted = vlsr.to(u.MHz, equivalencies=relativistic_equiv)
    return f_shifted.value


def match_lines(potential_lines, detected_lines_frequency, tolerance):
    potential_frequency = np.array([pot_line[3] for pot_line in potential_lines])
    actual_lines = []
    for index, frequency in enumerate(detected_lines_frequency):
        distances = potential_frequency - frequency
        if min(abs(distances)) > tolerance:
            actual_lines.append([index, "U", "U", "0", "0"])
        else:
            for index_dist, dist in enumerate(distances):
                if dist < tolerance:
                    actual_lines.append([index] + potential_lines[index_dist])
    return actual_lines


def output_folder(output):
    print("Creating output folder...")
    isdir = os.path.isdir(output)
    if isdir:
        print(
            f"Folder {output} exists, the result files will be overwritten. Continue with new output folder? [y] or [n]"
        )
        proceed = input(">>>")
        if proceed == "y":
            print("Type new output folder name")
            new_output = input(">>>")
            os.makedirs(new_output)
        else:
            new_output = output
    else:
        new_output = output
        os.makedirs(new_output)
    return new_output


class Spectrum:
    """This is a spectrum class. Initialises with a text file."""

    def __init__(self, log_file):
        self.columns = np.loadtxt(
            log_file,
            skiprows=3,
            max_rows=1,
            comments=None,
            dtype="str",
            usecols=(3, 4, 5),
        )
        self.frequency, self.velocity, self.flux = np.loadtxt(
            log_file, usecols=(2, 3, 4), unpack=True
        )
        self.frequency_resolution = self.frequency[1] - self.frequency[0]
        self.velocity_resolution = self.velocity[1] - self.velocity[0]

    def potential_lines(self, list_file, vlsr):
        print("Finding expected lines in the spectrum...")
        transition_frequencies = np.loadtxt(list_file, usecols=[1])
        species, transitions = np.loadtxt(
            list_file, usecols=(0, 2), dtype="str", unpack=True
        )
        minimum, *_, maximum = sorted(self.frequency)
        print("\t Redshifting teorical frequencies...")
        redshifted_frequencies = redshift_frequency(transition_frequencies, vlsr)
        potential_lines = []
        for index, frequency in enumerate(redshifted_frequencies):
            if minimum <= frequency <= maximum:
                potential_lines.append(
                    [
                        species[index],
                        transitions[index],
                        transition_frequencies[index],
                        frequency,
                    ]
                )
        if len(potential_lines) == 0:
            exit(
                "There is no potential lines in the frequency range of the spectrum. Edit the file <<lines.txt>>."
            )
        return potential_lines

    @property
    @lru_cache(10)
    def rms(self):
        print("\tFinding rms of the spectrum...")
        values, edges = np.histogram(self.flux, bins=100)
        popt, _ = curve_fit(gaussian, edges[:-1], values, p0=[max(self.flux), 0, 1])
        return abs(popt[-1])

    def find_lines(self, snr, width):
        print("Finding detected lines in the spectrum...")
        separation = width / abs(self.velocity_resolution)
        peaks = sig.find_peaks(self.flux, height=snr * self.rms, distance=separation)
        position_peaks = peaks[0]
        return (
            self.frequency[position_peaks],
            self.velocity[position_peaks],
            self.flux[position_peaks],
        )

    def write_parameters(
        self, actual_lines, peak_frequency, peak_velocity, peak_flux, output
    ):
        print("Writing output file...")
        header = (
            "Peak\tSpecies\tTransition\tTeorical_Frequency\tRedshifted_Frequency\t"
            + f"Peak_{self.columns[0]}\tPeak_{self.columns[1]}\tPeak_{self.columns[2]}"
        )
        peaks = np.array([i[0] for i in actual_lines])
        molecules = np.array([i[1] for i in actual_lines])
        transitions = np.array([i[2] for i in actual_lines])
        frequencies = np.array([i[3] for i in actual_lines])
        redshifted_frequencies = np.array([i[4] for i in actual_lines])
        peak_frequencies = [peak_frequency[p] for p in peaks]
        peak_velocities = [peak_velocity[p] for p in peaks]
        peak_fluxes = [peak_flux[p] for p in peaks]
        # format of columns in data
        columns_dtype = [
            ("peak", "int32"),
            ("molecule", "U25"),
            ("transition", "U25"),
            ("frequency", float),
            ("redshifted_frequency", float),
            ("peak_frequency", float),
            ("peak_velocity", float),
            ("peak_flux", float),
        ]
        fmt = ["%i"] + ["%s"] * 2 + ["%f"] * 5
        # write data
        data = np.zeros(molecules.size, dtype=columns_dtype)
        data["peak"] = peaks
        data["molecule"] = molecules
        data["transition"] = transitions
        data["frequency"] = frequencies
        data["redshifted_frequency"] = redshifted_frequencies
        data["peak_frequency"] = peak_frequencies
        data["peak_velocity"] = peak_velocities
        data["peak_flux"] = peak_fluxes
        np.savetxt(output + "/detected_lines.txt", data, header=header, fmt=fmt)

    # this is just for reference while I code
    def make_plot(self, log_file, lines, frequency_peaks, flux_peaks, output):
        print("Making plot...")
        fig, ax = plt.subplots()
        # plot the spectrum
        ax.plot(self.frequency, self.flux, label="data")
        # plot the peaks
        ax.scatter(frequency_peaks, flux_peaks, c="r")
        x_lims = ax.get_xlim()
        ax.hlines(self.rms, x_lims[0], x_lims[1])
        ax.annotate(
            f"rms = {self.rms:.2f}",
            (x_lims[0], self.rms + self.rms / 10),
            xycoords="data",
        )
        # plot the potential lines
        y_lims = ax.get_ylim()
        for l in lines:
            if l[1] == "U":
                ax.vlines(
                    frequency_peaks[l[0]],
                    y_lims[0],
                    y_lims[1],
                    colors="r",
                    linestyles="dashed",
                )
                ax.annotate(
                    l[1], (frequency_peaks[l[0]], flux_peaks[l[0]]), xycoords=("data")
                )
            else:
                ax.vlines(l[4], y_lims[0], y_lims[1], "b")
                ax.annotate(
                    " ".join([l[1], l[2]]),
                    (l[3], 0.9),
                    xycoords=("data", "axes fraction"),
                )
        ax.legend()
        # add exis labels
        ax.set_xlabel(self.columns[0])
        ax.set_ylabel(self.columns[-1])
        fig.savefig(output + "/" + log_file[:-4] + ".png", bbox_inches="tight")
