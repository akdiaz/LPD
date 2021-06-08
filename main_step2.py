import check_line

spectrum_name='spectrum_golden.txt'
list_file='lines.txt'
spectrum = check_line.Spectrum(spectrum_name)
lines = spectrum.potential_lines(list_file)
rms, frequency_peaks, flux_peaks = spectrum.find_lines()
spectrum.make_plot(spectrum_name, lines, rms, frequency_peaks, flux_peaks)
