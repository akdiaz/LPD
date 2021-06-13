import check_line

#need to couple name of spectrum in both scripts?
spectrum_name='spectrum_golden_joined.txt'
list_file='lines.txt'
spectrum = check_line.Spectrum(spectrum_name)
lines = spectrum.potential_lines(list_file)
print(f'>>>> Potential lines are {lines}')
rms, frequency_peaks, flux_peaks = spectrum.find_lines()
popt, pcov = spectrum.get_line_parameters(flux_peaks, frequency_peaks, 50)
print(f'>>>> Fitted parameters are {popt}, {pcov}')
actual_lines = spectrum.match_lines(lines, popt, 1.5)
print(f'>>>> Actual lines are {actual_lines}')
spectrum.write_parameters(actual_lines, popt, pcov)
spectrum.make_plot(spectrum_name, actual_lines, rms, frequency_peaks, flux_peaks, popt)
