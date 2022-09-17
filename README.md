# LPD
Lines in Protoplanetary Disks. ALMA Archive High Level Data Products.

**URL**: [akdiaz.xyz/memoir](akdiaz.xyz/memoir)

## Molecular EMissiOn IdentifieR (MEMOIR)

`MEMOIR` detects the lines present in a spectrum and identifies them by comparing their frequencies against those of *known-lines*. **This is a preliminary identification; use at your own risk.**

Needs a spectrum file (formatted like the ones generated by [CASA](https://casa.nrao.edu/)) and a CSV file with the *known-lines* (formatted like those generated by [Splatalogue](https://splatalogue.online//)). `MEMOIR` uses by default [a built-in list](https://github.com/akdiaz/LPD/blob/main/src/memoir/data/allmols_combined_transitions.csv) generated using these [commands](https://github.com/aida-ahmadi/freqcomb/blob/master/examples/lines_in_PPDs.py) of [`FreqComb`](https://github.com/aida-ahmadi/freqcomb). Some transitions in this file are in fact a combination of transitions, please, check the [`grouping of lines`](https://github.com/aida-ahmadi/freqcomb/tree/master/tables).


### Installation

```bash
❯ pip install memoir-lpd
```

### Usage

`MEMOIR` has three subcommands: `extract`, to extract a spectrum from a cube; `estimate`, to estimate the velocity and width of the peaks in a spectrum; and `identify`, to detect and identify the lines in a spectrum.

You can access `MEMOIR` help with 

```
❯ memoir -h
```

which produces

```
usage: memoir [-h] [-v] {extract,estimate,identify} ...

MEMOIR: Molecular EMissiOn IdentifieR. Searches for lines in a spectrum and assignes IDs by comparing their frequencies
with those of known lines. Returns a file text with the ID and the peak values (frequency, velocity, intensity/flux) of
the detected lines.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

subcommands:
  valid subcommands

  {extract,estimate,identify}
                        type memoir <<subcommand>> -h to get additional help
```

## Extracting spectra

In the directory where your cube.FITS and mask.FITS files are stored, run:

```
❯ memoir extract
```

This will produce a text file end-named "spectrum.txt" with the spectrum taken in cube.FITS, using the mask mask.FITS. If you pass several cubes and masks (see [examples](#examples)) to the command, you will get one spectrum file per cube&amp;mask pair. 

There are a few options you can set to control the behavior of `MEMOIR` while extracting spectra. You can view them with

```
❯ memoir extract -h
```

which produces

```
usage: memoir extract [-h] [-i FITS_IMAGE [FITS_IMAGE ...]]
                      [-m FITS_MASK [FITS_MASK ...]]

extracts a spectrum from a fits image (provided by -i) using a mask image (provided by -m) and writes it to disk with
end-name 'spectrum.txt'.

optional arguments:
  -h, --help            show this help message and exit
  -i FITS_IMAGE [FITS_IMAGE ...], --fits_image FITS_IMAGE [FITS_IMAGE ...]
                        Fits image to take spectrum on mask <<fits_mask>>. (default: [''])
  -m FITS_MASK [FITS_MASK ...], --fits_mask FITS_MASK [FITS_MASK ...]
                        Mask used to take spectrum in image <<fits_image>>. (default: [''])

```

### How it works

1. If the mask is all blank, skips to the next image and mask provided.
2. The mask can have different masking in each channel, so `MEMOIR` constructs a new joint mask that is the union of the masks in all channels and uses it to take the spectrum.
3. The spectrum extracted using the joint mask is written to disk in a text file end-named "spectrum.txt".

## Estimating a velocity and width for the peaks

In the directory where your spectrum file is stored, run:

```
❯ memoir estimate
```

This will produce a text file (called "estimate.txt") with the properties (index, velocity, flux/intensity and width at 10% of maximum) of the peaks detected in the spectrum. If you pass several spectra to the script, you will get only one file with the information of all the peaks detected. The *index* of the peak includes a reference to the spectrum on which it was found.

For example, if you analyse the spectra in the input files "spw_0.txt" (containing one peak) and "spw_3.txt" (containing two peaks), you will get an output text file (named "estimate.txt") like this:

```
# Spectrum_Peak_ID	Peak_Velocity_(km/s)	Peak_Sum_(Jy/beam)	Peak_Width_10% (km/s)
spw_0_0 4.621650 84.846497 6.848417
spw_3_0 45.017431 7.240037 12.464653
spw_3_1 -24.578994 7.425170 12.936669
```
There are several options you can set to control the behaviour of `MEMOIR` while estimating these values. You can view them with

```
❯ memoir estimate -h
```

which produces

```
usage: memoir estimate [-h] [-s SPECTRUM_FILE_NAME [SPECTRUM_FILE_NAME ...]] [--snr SNR] [-w LINE_WIDTH]

Detects peaks in a spectrum (provided by -s) and estimate their velocity and width (at 10% of maximum). Writes to 
disk a file with the relevant info in the working directory.

optional arguments:
  -h, --help            show this help message and exit
  -s SPECTRUM_FILE_NAME [SPECTRUM_FILE_NAME ...], --spectrum_file_name SPECTRUM_FILE_NAME [SPECTRUM_FILE_NAME ...]
                        Name of the file (including extension) with the spectrum to analyse. If not set (default 
                        behaviour) will use all the files in the working directory end-named 'spectrum.txt'.
                        (default: [''])
  --snr SNR             Signal-to-noise ratio. Only peaks with flux higher than <<SNR>> will be returned (default: 5)
  -w LINE_WIDTH, --line_width LINE_WIDTH
                        Line width prior to estimation (in the velocity units of the input spectrum). Local peaks closer
                        than <<line_width>> will be considered as belonging to the same line, and only the one with
                        higher flux will be returned. (default: 20)

```

### How it works

1. Finds the peaks in the spectrum whose values are above a certain threshold (provided by --snr) and that are separated in velocity more than certain value (provided by -w).
2. Finds the peak-velocity and peak-width at 10% of the maximum value.
4. Returns the output file (see above).

## Detecting and identifying the lines

In the directory where your spectrum file is stored, run:

```
❯ memoir identify
```

This will produce a text file (called "detected_lines.txt") with the identified lines and their peak properties (index, velocity, frequency and flux/intensity), and a plot (a .png file with the same name of the input spectrum file) with useful information, both inside a subfolder named "output" by default. If you pass several spectra to the script, you will get one plot per spectrum but only one file with the information of all the lines detected. The *index* of the lines includes a reference to the spectrum on which they were found.

For example, if you analyse the spectra in the input files "spw_0.txt" and "spw_3.txt" (containing one CO line each), you will get an output text file (named "detected_lines.txt") like this:

```
# Spectrum_Peak_ID	Species	Transition	Teorical_Frequency	Redshifted_Frequency	Peak_frequency_(MHz)	Peak_Velocity_(km/s)	Peak_Flux_density_(Jy)
spw0_0 13COv=0 J=3-2,F=5/2-5/2 330587.867100 330587.867100 330587.387762 0.528000 7.513535
spw0_0 13COv=0 J=3-2,F=5/2-3/2 330587.949000 330587.949000 330587.387762 0.528000 7.513535
spw0_0 13COv=0 3-2 330587.965300 330587.965300 330587.387762 0.528000 7.513535
spw0_0 13COv=0 J=3-2,F=7/2-5/2 330587.981600 330587.981600 330587.387762 0.528000 7.513535
spw3_0 COv=0 3-2 345795.989900 345795.989900 345795.840051 0.130000 53.377550
```
and two plots like these (named "spw_0.png" and "spw_3.png"):

![spw_0](https://github.com/akdiaz/LPD/blob/main/Help/spw0.png?raw=True "spw_0")

![spw_3](https://github.com/akdiaz/LPD/blob/main/Help/spw3.png?raw=True "spw_3")

In this case, `MEMOIR` found one line (spw0_0) that could be any of the 13COv=0 listed, and another one (spw3_0) identified as COv=0 3-2, whose peaks are marked in the plot as red dots, and the frequency of the posible lines are marked with blue lines.

There are several options you can set to control the behavior of `MEMOIR` while identifying the lines. You can view them with

```
❯ memoir identify -h
```
which produces

```
usage: memoir identify [-h] [-s SPECTRUM_FILE_NAME [SPECTRUM_FILE_NAME ...]] [-e ESTIMATE_FILE_NAME]
                            [-l KNOWN_LINES_FILE_NAME] [-o OUTPUT] [--snr SNR] [-w LINE_WIDTH] 
                            [-t FREQUENCY_TOLERANCE] [--vlsr VLSR]

Detects lines in a spectrum (provided by -s) and identifies them by comparing their frequencies with those in a
known-lines file (provided by -l). Writes to disk a file and plot(s) with the relevant info in the folder <<output>>.

optional arguments:
  -h, --help            show this help message and exit
  -s SPECTRUM_FILE_NAME [SPECTRUM_FILE_NAME ...], --spectrum_file_name SPECTRUM_FILE_NAME [SPECTRUM_FILE_NAME ...]
                        Name of the file (including extension) with the spectrum to analyse. If not set (default
                        behaviour) will use all the files in the working directory end-named 'spectrum.txt'.
                        (default: [''])
  -e ESTIMATE_FILE_NAME, --estimate_file_name ESTIMATE_FILE_NAME
                        Name of the file (including extension) with estimates of the velocity and width (at 10% of
                        maximum) of the peaks in the spectrum. If not set (default behaviour) will use, if exists,
                        a file in the working directory named 'estimate.txt', or the values set with the parameters
                        --vlsr and --line_width, in that order of preference. (default: [''])
  -l KNOWN_LINES_FILE_NAME, --known_lines_file_name KNOWN_LINES_FILE_NAME
                        Name of the file (including extension) with the known lines. If not specified, use memoir's
                        built-in one. (default: None)
  -o OUTPUT, --output OUTPUT
                        Name of the output folder. (default: output)
  --snr SNR             Signal-to-noise ratio. Only peaks with flux higher than <<SNR>> will be returned (default: 5)
  -w LINE_WIDTH, --line_width LINE_WIDTH
                        Line width (in the velocity units of the input spectrum). Local peaks closer than <<line_width>>
                        will be considered as belonging to the same line, and only the one with higher flux will be
                        returned. (default: 20)
  -t FREQUENCY_TOLERANCE, --frequency_tolerance FREQUENCY_TOLERANCE
                        Frequency tolerance (in the frequency units of the input spectrum). If a detected line has a 
                        known line with a frequency separation less than <<frequency_tolerance>>, it will assume its 
                        ID, if not, will remain unidentified (U). (default: 0.01)
  --vlsr VLSR           Source radial velocity (local standard of rest) in km/s. (default: 0)

```

### How it works

1. If a text file with estimates of peak velocities and widths **exists, or is provided** (by -e), assumes as the source radial velocity in the local standard of rest (vlsr) the velocity of the peak closer to 0 km/s (using as rest-frequency the central frequency of the spectrum, assumed to be in GHz), and as line-width (w) the mean of the widths of all the peaks. If this file **does not exist**, uses the vlsr and line-width provided by the user with the parameters --vlsr and -w, respectively (or their default values).
2. Finds the lines in the spectrum whose peaks are above a certain threshold (provided by --snr) and that are separated in velocity more than certain value (provided by -w). These are the *detected-lines*.
3. Looks up in the csv file containing the *known-lines* and
   - redshifts the theoretical frequencies according the velocity of the source (provided by --vlsr).
   - finds those lines that have redshifted frequencies inside the frequency range of the spectrum. These are the *expected-lines*.
4. Matches each *detected-line*, with **all** the *expected-lines* that are closer in frequency than certain value (provided by -t).
5. Returns the output files (see above).

## Examples

**Extracting spectra:**
```
❯ memoir extract
```
will make `MEMOIR` extract spectra in all the FITS end-named "pbcor.fits" using the corresponding mask end-named "mask.fits" in your current working directory. The spectra will be written to disk in a file end-named "spectrum.txt".

```
❯ memoir extract -i cube.fits -m mask.fits
```
will make `MEMOIR` take a spectrum in "cube.fits" using the mask "mask.fits" in your current working directory. The spectrum will be written to disk in a file named "cube.spectrum.txt".

```
❯ memoir extract -i cube1.fits cube2.fits  -m mask1.fits mask2.fits
```
will make `MEMOIR` take a spectrum in "cube1.fits" using the mask "mask1.fits", and in "cube2.fits" using the mask "mask2.fits", in your current working directory. The spectra will be written to disk in two files named "cube1.spectrum.txt" and "cube2.spectrum.txt". You can use as many cubes and corresponding masks as desired.

**Estimating a velocity and width for the peaks:**
```
❯ memoir estimate
```
will make `MEMOIR` detect the peaks in all the files end-named "spectrum.txt" in your current working directory, and find their velocity and width at 10% of the maximum. This info will be written to disk in a file named "estimate.txt". Be mindful when processing more than one spectrum at the same time, since all the info in the output file will be later used as input parameters for the subcommand `identify` (see [how it works](### How it works)).

```
❯ memoir estimate -s spw0.txt
```
will make `MEMOIR` detect and estimate the properties of the peaks in the file "spw0.txt" in your current working directory.

```
❯ memoir estimate -s spw0.txt spw3.txt
```
will make `MEMOIR` detect and estimate the properties of the peaks in the files "spw0.txt" and "spw3.txt" in your current working directory.

```
❯ memoir estimate -s *.txt
```
will make `MEMOIR` detect and estimate the properties of the peaks in all the .txt files in your current working directory.


**Detecting and identifying lines:**

```
❯ memoir identify
```
will make `MEMOIR` detect and identify the lines in all the files end-named "spectrum.txt" in your current working directory. If an estimate.txt file exists in the working directory, it will use the info there to estimate the vlsr and line-width (see above).

```
❯ memoir identify -e "my_estimate.txt"
```
will make `MEMOIR` detect and identify the lines in all the files end-named "spectrum.txt" in your current working directory. It will use the info in the file "my_estimate.txt" to estimate the vlsr and line-width (see above).

```
❯ memoir identify --vlsr 5 -w 10 
```
will make `MEMOIR` detect and identify the lines in all the files end-named "spectrum.txt" in your current working directory. If an estimate.txt file **does not exist** in the working directory, it will use as vlsr and line width the values set by the user (or their default, if not set). If the estimate.txt file **does** exist, it will use it even if the user has set --vlsr and/or -w. 

```
❯ memoir identify -s spw0.txt
```
will make `MEMOIR` detect and identify the lines in the file "spw0.txt" in your current working directory. 

```
❯ memoir identify -s spw0.txt spw3.txt
```
will make `MEMOIR` detect and identify the lines in the files "spw0.txt" and "spw3.txt" in your current working directory.

```
❯ memoir identify -s *.txt
```
will make `MEMOIR` detect and identify the lines in `MEMOIR` in all the .txt files in your current working directory.

**Example of spectrum file**:
```
# spw0.image, region=
# beam size: 17.262405172558292 arcsec2, 53.13144097434767 pixels
# Total flux: 7.47938294096 Jy.MHz
# Channel number_of_unmasked_pixels frequency_(MHz) Velocity_(km/s) Flux_density_(Jy)
        0                       269   330598.997228       -9.999833     -9.647420e-01
        1                       269   330598.961941       -9.967834     -1.071281e+00
        2                       269   330598.926653       -9.935835     -3.810407e-01
        3                       269   330598.891366       -9.903836     -4.499658e-01
        4                       269   330598.856079       -9.871837      5.284649e-01
        5                       269   330598.820792       -9.839839      4.755686e-01
```

**Example of known-lines file**:
```
Species,ChemicalName,QNs,Freq,log10_Aij,EU_K,CDMS/JPL Intensity
CNv=0,Cyanide Radical,"N=1-0,J=1/2-1/2,F=1/2-1/2",113.1233687,-5.89067,5.43004,-4.7119
CNv=0,Cyanide Radical,"N=1-0,J=1/2-1/2,F=1/2-3/2",113.14419,-4.9776,5.43003,-3.7989
CNv=0,Cyanide Radical,"N=1-0,J=1/2-1/2,F=3/2-1/2",113.170535,-5.28862,5.43231,-3.809
CNv=0,Cyanide Radical,"N=1-0,J=1/2-1/2,F=3/2-3/2",113.191325,-5.17514,5.4323,-3.6956
CNv=0,Cyanide Radical,"N=1-0,J=3/2-1/2,F=5/2-3/2",113.490985,-4.92358,5.44668,-3.2691
CNv=0,Cyanide Radical,"N=1-0,J=3/2-1/2,F=1/2-1/2",113.499643,-4.97352,5.4481,-3.7962
CNv=0,Cyanide Radical,"N=1-0,J=3/2-1/2,F=3/2-3/2",113.508934,-5.28472,5.44754,-3.8064
CNv=0,Cyanide Radical,"N=1-0,J=3/2-1/2,F=1/2-3/2",113.5204215,-5.88634,5.44809,-4.7091
CNv=0,Cyanide Radical,"N=2-1,J=3/2-3/2,F=1/2-1/2",226.2874265,-4.98737,16.30806,-4.1215
CNv=0,Cyanide Radical,"N=2-1,J=3/2-3/2,F=3/2-1/2",226.3030784,-5.37977,16.30881,-4.2129
CNv=0,Cyanide Radical,"N=2-1,J=3/2-3/2,F=3/2-3/2",226.31454,-5.00405,16.30893,-3.8372
CNv=0,Cyanide Radical,"N=2-1,J=3/2-3/2,F=3/2-5/2",226.3325364,-5.34151,16.30893,-4.1747
CNv=0,Cyanide Radical,"N=2-1,J=3/2-3/2,F=5/2-3/2",226.3419306,-5.50078,16.31025,-4.1579
CNv=0,Cyanide Radical,"N=2-1,J=3/2-3/2,F=5/2-5/2",226.359871,-4.79365,16.31024,-3.4508
CNv=0,Cyanide Radical,"N=2-1,J=3/2-1/2,F=1/2-3/2",226.6165554,-4.96955,16.30818,-4.1043
CNv=0,Cyanide Radical,"N=2-1,J=3/2-1/2,F=3/2-3/2",226.63219,-4.37065,16.30893,-3.2044
CNv=0,Cyanide Radical,"N=2-1,J=3/2-1/2,F=5/2-3/2",226.659575,-4.02379,16.31024,-2.6815
CNv=0,Cyanide Radical,"N=2-1,J=3/2-1/2,F=3/2-1/2",226.679382,-4.27836,16.30889,-3.1122
CNv=0,Cyanide Radical,"N=2-1,J=5/2-3/2,F=7/2-5/2",226.874745,-3.94188,16.33495,-2.4751
CNv=0,Cyanide Radical,"N=2-1,J=5/2-3/2,F=5/2-5/2",226.892119,-4.74221,16.33579,-3.4004
CNv=0,Cyanide Radical,"N=2-1,J=5/2-3/2,F=3/2-5/2",226.9053771,-5.94809,16.33642,-4.7824
```
**Example of estimate file**:
```
# Spectrum_Peak_ID	Peak_Velocity_(km/s)	Peak_Sum_(Jy/beam)	Peak_Width_10% (km/s)
spw_0_0 4.621650 84.846497 6.848417
spw_1_0 6.072116 526.122437 4.316900
spw_2_0 45.017431 7.240037 12.464653
spw_2_1 -24.578994 7.425170 12.936669
spw_3_0 6.761816 15.532443 11.558561
spw_4_0 6.801448 17.015665 12.467995
spw_5_0 4.420516 24.261328 24.365458
spw_6_0 4.537041 10.090816 9.376807
```
Note that there are two peaks detected in the spectrum called "spw_2.txt" (the ones with IDs "spw_2_0" and "spw_2_1").

**Example of a detected_lines file**:
```
# Some transitions in the built-in file used for the identification of the lines are in fact a combination of transitions. Please check https://github.com/aida-ahmadi/freqcomb/tree/master/tables for the grouping done.
# This is a preliminary identification. Use at your own risk.
# Using vlsr = 4.420516 (km/s) and line_width = 11.791932500000001 (km/s).
# Spectrum_Peak_ID	Species	Transition	Teorical_Frequency	Redshifted_Frequency	Peak_Frequency_(GHz)	Peak_Velocity_(km/s)	Peak_Sum_(Jy/beam)	Peak_Width_FWHM (km/s)
spw_0_0 13COv=0 2-1 220.398676 220.395427 220.395286 4.621650 84.846497 6.848417
spw_0_0 CH3OHvt=0-2 10(-5)-11(-4)E2vt=0 220.401317 220.398067 220.395286 4.621650 84.846497 6.848417
spw_1_0 COv=0 2-1 230.538000 230.534601 230.533331 6.072116 526.122437 4.316900
spw_2_0 CCHv=0 N=3-2,J=7/2-5/2,F=4-3 262.004227 262.000363 262.000652 45.017431 7.240037 12.464653
spw_2_1 CCHv=0 N=3-2,J=5/2-3/2,F=3-2 262.064843 262.060979 262.061484 -24.578994 7.425170 12.936669
spw_3_0 C18O 2-1 219.560357 219.557119 219.555406 6.761816 15.532443 11.558561
spw_4_0 H2CO 3(0,3)-2(0,2) 218.222192 218.218974 218.217241 6.801448 17.015665 12.467995
spw_5_0 HCNv=0 J=3-2 265.886180 265.882259 265.882510 4.420516 24.261328 24.365458
spw_6_0 HCO+v=0 1-0 89.188523 89.187208 89.187176 4.537041 10.090816 9.376807
```
Note that the line with ID "spw_0_0" has two possible identifications (13COv=0 or CH3OHvt=0-2).

[![Black badge](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI badge](https://img.shields.io/pypi/v/memoir-lpd?color=blue)](https://pypi.org/project/memoir-lpd/)
