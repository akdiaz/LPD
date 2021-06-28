# to be run inside CASA 6.1
import sys, os
import argparse
import glob


sys.path.append(os.getcwd())  # to be able to find check_line
import get_spectrum

if __name__ == "__main__":

    image_name = glob.glob('*.image.pbcor.fits')
    
    for cube_name in image_name:
        base_name = cube_name[:-17]
        mask_name = base_name+".mask.fits"
        spectrum_name = base_name+".spectrum.txt"
        print(f"For {base_name}...")
        cube = get_spectrum.ImageCube(base_name)
        cube.get_spectrum()
