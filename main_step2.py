import check_line

#need to couple name of spectrum in both scripts?
spectrum_name='spectrum_spw0.txt'
list_file='lines.txt'
spectrum = check_line.Spectrum(spectrum_name)
lines = spectrum.potential_lines(list_file)
peak_frequencies, peak_velocities, peak_fluxes = spectrum.find_lines()
actual_lines = check_line.match_lines(lines, peak_frequencies)
spectrum.write_parameters(actual_lines, peak_frequencies, peak_velocities, peak_fluxes)
spectrum.make_plot(spectrum_name, actual_lines, peak_frequencies, peak_fluxes)
