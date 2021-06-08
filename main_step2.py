import check_line

spectrum_name='spectrum_golden.txt'
list_file='lines.txt'
spect = check_line.Spectrum(spectrum_name)
lines = spect.potential_lines(list_file)
spect.make_plot(spectrum_name, lines)
spect.find_lines()
