#!/usr/bin/python3

import logging
import sys
import os
from pathlib import Path
import subprocess
from shutil import copyfile, rmtree
from astropy.io import fits

def setup_logging():
    """Configure logging with appropriate format and level."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def clean_tmp_dir(tmp_dir):
    """Safely create a clean temporary directory."""
    rmtree(tmp_dir, ignore_errors=True)
    os.makedirs(tmp_dir, exist_ok=True)

def is_already_solved(fits_file):
    """Check if the FITS file already has WCS solution."""
    try:
        with fits.open(fits_file, ignore_missing_end=True) as hdu:
            return 'CRVAL1' in hdu[0].header and 'CD1_1' in hdu[0].header
    except Exception as e:
        logging.error(f"Error checking if {fits_file} is solved: {str(e)}")
        return False

def get_fits_info(fits_file):
    """Extract necessary information from FITS header."""
    with fits.open(fits_file, ignore_missing_end=True) as hdulist:
        header = hdulist[0].header
        ra = header['OBJCTRA'].strip().replace(' ', ':')
        dec = header['OBJCTDEC'].strip().replace(' ', ':')
        focal_length = header.get('FOCALLEN', 1800)
        binning = header['XBINNING']
        pixel_size = header['PIXSIZE1']
        arcsec_per_pixel = (pixel_size / focal_length) * 206.3 * binning

        return {
            'ra': ra,
            'dec': dec,
            'focal_length': focal_length,
            'arcsec_per_pixel': arcsec_per_pixel
        }

def solve_field(temp_file):
    """Run astrometry.net solve-field command."""
    cmd = [
        'solve-field',
        '--no-verify',
        '--no-plots',
        '--resort',
        '--downsample', '2',
        '-O',
        '-L', '26.586',
        '-H', '35.259',
        '-u', 'aw',
        temp_file
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"solve-field failed: {e.stderr}")
        return False
    except Exception as e:
        logging.error(f"Error running solve-field: {str(e)}")
        return False

def process_fits_file(fits_path, tmp_dir):
    """Process a single FITS file."""
    fits_path = Path(fits_path)
    if not fits_path.exists():
        logging.error(f"File not found: {fits_path}")
        return False

    if not fits_path.suffix.lower() == '.fits':
        logging.error(f"Not a FITS file: {fits_path}")
        return False

    try:
        if is_already_solved(fits_path):
            logging.info(f"File already solved: {fits_path}")
            return True

        clean_tmp_dir(tmp_dir)
        temp_file = Path(tmp_dir) / fits_path.name
        copyfile(fits_path, temp_file)

        logging.debug(f"Processing: {fits_path}")
        fits_info = get_fits_info(temp_file)
        logging.debug(f"Focal length: {fits_info['focal_length']}")
        logging.debug(f"Arc-sec per pixel: {fits_info['arcsec_per_pixel']:.2f}")
        logging.debug(f"RA: {fits_info['ra']}, Dec: {fits_info['dec']}")

        if solve_field(temp_file):
            new_file = temp_file.with_suffix('.new')
            if new_file.exists():
                copyfile(new_file, fits_path)
                logging.info(f"Successfully solved: {fits_path}")
                return True
            else:
                logging.error(f"Solved file not found: {new_file}")
                return False
        else:
            logging.warning(f"Could not solve: {fits_path}")
            return False

    except Exception as e:
        logging.error(f"Error processing {fits_path}: {str(e)}")
        return False

def main():
    """Main function to process FITS files."""
    setup_logging()
    tmp_dir = '/tmp/solver'

    if len(sys.argv) > 1:
        files = sys.argv[1:]
    # If receiving from pipe/stdin
    else:
        files = [line.strip() for line in sys.stdin]

    if not files:
        logging.error("No input files provided")
        sys.exit(1)

    success_count = 0
    total_files = len(files)

    for fits_file in files:
        if process_fits_file(fits_file, tmp_dir):
            success_count += 1

    logging.info(f"Processing complete: {success_count}/{total_files} files successfully solved")

if __name__ == "__main__":
    main()