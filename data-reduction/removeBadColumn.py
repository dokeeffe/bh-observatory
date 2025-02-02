import sys
import logging
from astropy.io import fits
#
# Cleaner script to remove the rightmost column from a FITS image. This right column is an artifact of the callibration process and should be removed.
# Example usage: find ~/Pictures/CalibratedLight -type f -mmin -60 -name "*.fits" | xargs python removeBadColumn.py
#

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def remove_bad_column(input_fits, side='right'):
    """
    Remove the rightmost or leftmost column from a FITS image and save the result.
    This right column is an artifact of the callibration process and should be removed.

    Parameters:
    -----------
    input_fits : str
        Path to input FITS file to be updated
    side : str, optional
        Which side to remove column from ('right' or 'left', default is 'right')
    """
    # Open the FITS file
    with fits.open(input_fits) as hdul:
        # Make a copy of the header
        header = hdul[0].header

        # Get the data and remove the bad column
        data = hdul[0].data

        # Remove column based on side parameter
        if side == 'right':
            cleaned_data = data[:, :-1]  # All columns except the last one
        else:  # 'left'
            cleaned_data = data[:, 1:]  # All columns except the first one

        if 'Removed bad column on right side' in header['COMMENT']:
            logging.warning(f"Bad column already removed from {input_fits}")
            return
        print(header['NAXIS1'])
        # Update the NAXIS1 keyword in header to reflect new size
        header['NAXIS1'] = cleaned_data.shape[1]
        header['COMMENT'] = 'Removed bad column on right side'
        # Create new FITS file with cleaned data
        fits.writeto(input_fits, cleaned_data, header, overwrite=True)


def process_file(filepath):
    """Process a single file."""
    try:
        remove_bad_column(filepath)
        logging.info(f"Cleaned bad col from: {filepath}")
    except Exception as e:
        logging.error(f"Error processing {filepath}: {e}")


def main():
    # If arguments were passed directly
    if len(sys.argv) > 1:
        for filepath in sys.argv[1:]:
            process_file(filepath)
    # If receiving from pipe/stdin
    else:
        for line in sys.stdin:
            filepath = line.strip()
            process_file(filepath)


if __name__ == "__main__":
    main()