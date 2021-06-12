import check_line

spectrum_name='spectrum_golden.txt'
list_file='lines.txt'
spectrum = check_line.Spectrum(spectrum_name)
lines = spectrum.potential_lines(list_file)
rms, frequency_peaks, flux_peaks = spectrum.find_lines()

#need to fix this for several lines (list)
popt, pcov = spectrum.get_line_parameters(flux_peaks[0], frequency_peaks[0], 50)

actual_lines = spectrum.match_lines(lines, popt, 1.5)


spectrum.make_plot(spectrum_name, actual_lines, rms, frequency_peaks, flux_peaks, popt)