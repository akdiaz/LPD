# LPD
Line in Protoplanetary Disks. ALMA Advanced Archive Products.

First step:
 Run main_step1.py inside CASA 6.1 to take the spectrum in a cube image, in a region defined by a mask image. Needs the cube and the mask, both in FITS format.
 
Second step:
 Run main_step2.py in Python3 to recognize the lines in the spectrum. Need the spectrum file (created in previous step) and a file with 'known lines' for frequency comparison.
