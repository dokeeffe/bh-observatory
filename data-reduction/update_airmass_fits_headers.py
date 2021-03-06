#!/usr/bin/python3

import sys
from astropy.io import fits
import glob
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz

for pattern in sys.argv[1:]:
    for file in glob.glob(pattern):
        print(file)
        data, header = fits.getdata(file, header=True)
        ra_dec = '{} {}'.format(header['OBJCTRA'],header['OBJCTDEC'])
        coord = SkyCoord(ra_dec, unit=(u.hourangle, u.deg))
        bobs_location = EarthLocation(lat=52.253494*u.deg, lon=-8.360614*u.deg, height=75*u.m)
        time = Time(header['DATE-OBS'])
        altaz = coord.transform_to(AltAz(obstime=time,location=bobs_location))
        print(altaz.secz)

        header['AIRMASS'] = float(altaz.secz)
        header['GAIN'] = 0.4

        fits.writeto(file, data, header, clobber=True)
