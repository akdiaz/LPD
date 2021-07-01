import check_line
import argparse

parser = argparse.ArgumentParser(
    description="LineR: Line Recognizer. Searches for lines in a spectrum and assignes IDs by comparing their frequencies with those of known lines. Returns a file text with the ID and the peak values (frequency, velocity, flux) of the detected lines.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
    "-t",
    "--frequency_tolerance",
    type=float,
    help="Frequency tolerance (in the frequency units of the input spectrum). If a detected line has a known line with a frequency separation less than <<frequency_tolerance>>, it will assume its ID, if not, will remain unidentified (U).",
    default=2
)
parser.add_argument(
    "-w",
    "--line_width",
    type=float,
    help="Line width (in the velocity units of the input spectrum). Local peaks closer than <<line_width>> will be considered as belonging to the same line, and only the one with higher flux will be returned.",
    default=20,
)
parser.add_argument(
    "--snr",
    type=float,
    help="Signal-to-noise ratio. Only peaks with flux higher than <<SNR>> will be returned",
    default=5,
)
parser.add_argument(
    "-s",
    "--spectrum_file_name",
    type=str,
    nargs="+",
    help="Name of the file (including extension) with the spectrum to analyse.",
    default="spectrum_golden.txt",
)
parser.add_argument(
    "-l",
    "--known_lines_file_name",
    type=str,
    help="Name of the file (including extension) with the known lines.",
    default="lines.txt",
)
parser.add_argument(
    "-o",
    "--output",
    type=str,
    help="Name of the output folder.",
    default="output",
)
parser.add_argument(
    "--vlsr",
    type=float,
    help="Source radial velocity (local standard of rest) in km/s.",
    default=0,
)

if __name__ == "__main__":
    args = parser.parse_args()

    output = check_line.output_folder(args.output)

    for file_name in args.spectrum_file_name:
        print(f"For spectrum {file_name}:")
        spectrum = check_line.Spectrum(file_name)
        lines = spectrum.potential_lines(args.known_lines_file_name, args.vlsr)
        peak_frequencies, peak_velocities, peak_fluxes = spectrum.find_lines(
            args.snr, args.line_width
        )
        actual_lines = check_line.match_lines(
            lines, peak_frequencies, args.frequency_tolerance
        )
        spectrum.write_parameters(
            actual_lines,
            peak_frequencies,
            peak_velocities,
            peak_fluxes,
            output,
            file_name,
        )
        spectrum.make_plot(
            file_name, actual_lines, peak_frequencies, peak_fluxes, output
        )
