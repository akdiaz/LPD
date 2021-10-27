# to be run inside CASA 6.1
# execfile('get_spectrum_CASA.py')

import sys, os
import glob

script_directory = os.getcwd() 
sys.path.append(script_directory)  # to be able to find check_line
import get_spectrum


print(
     f"Looking for *image.pbcor.fits and *.mask.fits in current directory:\n\n{script_directory}\n\nDo you want to change directories? [y] or [n]"
     )
proceed = input(">>> ")
if proceed == 'y':
    data_directory = input(">>> Type directory path: ")
else: 
    data_directory = script_directory


os.chdir(data_directory)

print(
     f"Looking now in {data_directory}... "
     )

image_name = glob.glob("*.pbcor.fits")

if image_name == []:
    print(
         "No files found."
         )
else:
    for cube_name in image_name:
        base_name = cube_name[:-17]
        mask_name = base_name + ".mask.fits"
        spectrum_name = base_name + ".spectrum.txt"
        print(f"For {base_name}...")
        cube = get_spectrum.ImageCube(base_name)
        cube.get_spectrum()

os.chdir(script_directory)
