#!/usr/bin/env python3

from functools import lru_cache
from sys import exit
import glob
import os
import shutil

from astropy.io import fits
from scipy.optimize import curve_fit
import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.signal as sig


def gaussian(x, a, x0, sigma):
    y = a * np.exp(-((x - x0) ** 2) / (2 * sigma**2))
    return y


def make_union_mask(fits_mask):
    # import mask
    print("\t>>> Importing mask image...")
    hdul = fits.open(fits_mask)
    data = hdul[0].data[0]
    hdul.close()
    if np.amax(data) != 0:
        # union of masks in all channels
        print("\t>>> Making joint mask...")
        mask = np.sum(data, axis=0)
        mask[mask != 0] = 1
        region_pix = int(np.sum(mask))
        return region_pix, mask
    else:
        print("\t>>> This mask is all zeros. Moving on...")
        return False, False


def redshift_frequency(f, vlsr):
    """Assumes (for now) rest frequency (f) in GHz and velocity of the source (vlsr) in km/s."""
    f_rest = f * u.GHz  # rest frequency
    vlsr = vlsr * u.km / u.s  # velocity of the source
    radio_equiv = u.doppler_radio(f_rest)
    f_shifted = vlsr.to(u.GHz, equivalencies=radio_equiv)
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
                if abs(dist) <= tolerance:
                    actual_lines.append([index] + potential_lines[index_dist])
    return actual_lines


def spectrum_exist():
    spectrum_files = glob.glob("*spectrum.txt")
    if spectrum_files == []:
        return False
    else:
        return spectrum_files


def output_folder(output):
    print("Creating output folder...")
    isdir = os.path.isdir(output)
    if isdir:
        print(
            f"Folder {output} exists, the result files will be overwritten. Continue with new output folder? [y] or [n]"
        )
        proceed = input(">>> ")
        if proceed == "y":
            print("Type new output folder name")
            new_output = input(">>> ")
            os.makedirs(new_output)
        else:
            shutil.rmtree(output)
            new_output = output
            os.makedirs(new_output)
    else:
        new_output = output
        os.makedirs(new_output)
    return new_output


class Image:
    """This is an image class. Initialises with a fits image and a mask."""

    def __init__(self, fits_image, mask):
        self.mask = mask
        self.name = fits_image

    def get_spectrum(self, region_pix):
        # import image
        print("\t>>> Importing fits image...")
        hdul = fits.open(self.name)
        data_image = hdul[0].data[0]
        # get info from header
        beam_maj = hdul[0].header["BMAJ"]
        beam_min = hdul[0].header["BMIN"]
        beam_units = hdul[0].header["BUNIT"]
        delta_ra = hdul[0].header["CDELT1"]
        delta_dec = hdul[0].header["CDELT2"]
        delta_freq = hdul[0].header["CDELT3"]
        initial_freq = hdul[0].header["CRVAL3"]
        freq_units = hdul[0].header["CUNIT3"]
        channels = hdul[0].header["NAXIS3"]
        rest_freq = hdul[0].header["RESTFRQ"]
        hdul.close()
        # calculate beam
        beam_area = (
            np.pi / (4 * np.log(2)) * beam_maj * beam_min * 3600**2
        )  # arcsec^2
        pix_area = abs(delta_ra * delta_dec) * 3600**2  # arcsec^2
        beam_pix = beam_area / pix_area  # pixels
        # calculate sum inside mask
        print("\t>>> Taking spectrum...")
        spectrum = []
        for channel in data_image:
            intensity = np.nansum(channel * self.mask)
            spectrum.append(intensity)
        # generate freq column
        freq = (
            np.arange(initial_freq, initial_freq + channels * delta_freq, delta_freq)[
                :channels
            ]
            * 10**-9
            * u.GHz
        )
        # generate velocity column
        radio_equiv = u.doppler_radio(rest_freq * 10**-9 * u.GHz)
        velocity = freq.to(u.km / u.s, equivalencies=radio_equiv)
        # generate channel column
        chan = np.arange(channels)
        # generate pixels column
        pix = np.full(channels, region_pix)
        return chan, pix, freq.value, velocity.value, spectrum, beam_area, beam_pix

    def write_spectrum(self, chan, pix, freq, velocity, spectrum, beam_area, beam_pix):
        # spectrum_file
        output_file = self.name[:-4] + "spectrum.txt"
        # generate header
        header = f"{self.name}, region=\n\
beam size: {beam_area} arcsec2, {beam_pix} pixels\n\
Total flux: \n\
Channel number_of_unmasked_pixels Frequency_(GHz) Velocity_(km/s) Sum_(Jy/beam)"
        # format of columns in spectrum_file
        columns_dtype = [
            ("channel", int),
            ("pixels", int),
            ("frequency", float),
            ("velocity", float),
            ("sum", float),
        ]
        fmt = ["%i"] * 2 + ["%f"] * 3
        # write data in spectrum_file
        data = np.zeros(freq.size, dtype=columns_dtype)
        data["channel"] = chan
        data["pixels"] = pix
        data["frequency"] = freq
        data["velocity"] = velocity
        data["sum"] = spectrum
        # write spectrum_file
        print("\t>>> Writing spectrum to file...")
        np.savetxt(output_file, data, header=header, fmt=fmt)


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
        data = pd.read_csv(list_file)
        transition_frequencies = np.array(data.Freq)
        species = np.array(data.Species)
        transitions = np.array(data.QNs)
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
                "There are no expected lines in the frequency range of the spectrum."
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
        self, actual_lines, peak_frequency, peak_velocity, peak_flux, output, log_file
    ):
        print("Writing output file...")
        output_file = output + "/detected_lines.txt"
        header = (
            "Spectrum_Peak_ID\tSpecies\tTransition\tTeorical_Frequency\tRedshifted_Frequency\t"
            + f"Peak_{self.columns[0]}\tPeak_{self.columns[1]}\tPeak_{self.columns[2]}"
        )
        peaks = np.array([i[0] for i in actual_lines])
        name_peaks = np.array([log_file[:-4] + "_" + str(p) for p in peaks])
        molecules = np.array([i[1] for i in actual_lines])
        transitions = np.array([i[2] for i in actual_lines])
        frequencies = np.array([i[3] for i in actual_lines])
        redshifted_frequencies = np.array([i[4] for i in actual_lines])
        peak_frequencies = [peak_frequency[p] for p in peaks]
        peak_velocities = [peak_velocity[p] for p in peaks]
        peak_fluxes = [peak_flux[p] for p in peaks]
        # format of columns in data
        columns_dtype = [
            ("name_peak", "U100"),
            ("molecule", "U25"),
            ("transition", "U25"),
            ("frequency", float),
            ("redshifted_frequency", float),
            ("peak_frequency", float),
            ("peak_velocity", float),
            ("peak_flux", float),
        ]
        fmt = ["%s"] * 3 + ["%f"] * 5
        # write data
        data = np.zeros(molecules.size, dtype=columns_dtype)
        data["name_peak"] = name_peaks
        data["molecule"] = molecules
        data["transition"] = transitions
        data["frequency"] = frequencies
        data["redshifted_frequency"] = redshifted_frequencies
        data["peak_frequency"] = peak_frequencies
        data["peak_velocity"] = peak_velocities
        data["peak_flux"] = peak_fluxes
        if os.path.isfile(output_file):
            with open(output_file, "a") as f:
                np.savetxt(f, data, fmt=fmt)
        else:
            np.savetxt(output_file, data, header=header, fmt=fmt)

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
        fig.savefig(
            output + "/" + log_file.split("/")[-1][:-4] + ".png", bbox_inches="tight"
        )
