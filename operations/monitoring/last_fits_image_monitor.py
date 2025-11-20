#!/usr/bin/env python3

import sys
import json
import subprocess
from subprocess import CalledProcessError
import os
from astropy.io import fits
from astropy.visualization import ZScaleInterval, ImageNormalize
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def get_recent_image():
    try:
        return subprocess.check_output("find /home/dokeeffe/Pictures/Landed/ -type f -name '*.fits' -mmin -15 -printf '%T+ %p\n' | sort -r | head -n 1 | cut -d' ' -f2-", shell=True, text=True).strip()
    except CalledProcessError as e:
        sys.exit(1)

def convert_fits_to_jpeg(fits_file, output_name,  output_dir=None, cmap='viridis'):
    """
    Convert a FITS image to JPEG with auto-stretching using ZScale algorithm and add OBJECT text
    
    Args:
        fits_file (str): Path to the FITS file
        output_dir (str, optional): Directory to save the JPEG file. If None, save in the same directory
        cmap (str, optional): Colormap to use (default: 'viridis')
    
    Returns:
        str: Path to the saved JPEG file
    """
    try:
        # Open the FITS file
        with fits.open(fits_file) as hdul:
            # Get the header from the primary HDU
            header = hdul[0].header
            
            # Extract the OBJECT value if it exists
            object_name = header.get('OBJECT', 'Unknown Object')
            
            # Get other useful information if available
            date_obs = header.get('DATE-OBS', '')
            exposure = header.get('EXPTIME', '')
            filter_name = header.get('FILTER', '')
            
            # Get the data from the first HDU with data
            data = None
            for hdu in hdul:
                if hasattr(hdu, 'data') and hdu.data is not None:
                    data = hdu.data
                    break
            
            if data is None:
                print(f"No image data found in {fits_file}")
                return None
                
            # Handle different data dimensions
            if data.ndim > 2:
                # For data cubes or RGB, use the first slice/channel
                data = data[0] if data.ndim == 3 else data[0, 0]
            
            # Auto-stretching using ZScale
            zscale = ZScaleInterval()
            vmin, vmax = zscale.get_limits(data)
            norm = ImageNormalize(data, vmin=vmin, vmax=vmax)
            
            # Create the output filename
            base_name = os.path.basename(fits_file)
            jpeg_name = os.path.splitext(base_name)[0] + '.jpg'
            if output_name:
                jpeg_name = output_name

            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                jpeg_path = os.path.join(output_dir, jpeg_name)
            else:
                jpeg_path = os.path.join(os.path.dirname(fits_file), jpeg_name)
            
            # Plot and save the image
            plt.figure(figsize=(10, 10))
            plt.imshow(data, cmap=cmap, norm=norm, origin='lower')
            
            # Add the OBJECT name as text in the upper left corner
            plt.annotate(f"Object: {object_name}", xy=(0.02, 0.98), xycoords='axes fraction', 
                        fontsize=12, fontweight='bold', color='white', 
                        bbox=dict(boxstyle="round,pad=0.3", fc="black", alpha=0.7))
            
            # Add additional info if available
            info_text = []
            if date_obs:
                info_text.append(f"Date: {date_obs}")
            if exposure:
                info_text.append(f"Exp: {exposure}s")
            if filter_name:
                info_text.append(f"Filter: {filter_name}")
                
            # Add the additional info if we have any
            if info_text:
                plt.annotate("\n".join(info_text), xy=(0.02, 0.90), xycoords='axes fraction',
                            fontsize=10, color='white',
                            bbox=dict(boxstyle="round,pad=0.3", fc="black", alpha=0.7))
            
            # Add a timestamp of when the JPEG was created
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            plt.annotate(f"Processed: {timestamp}", xy=(0.02, 0.02), xycoords='axes fraction',
                        fontsize=8, color='white',
                        bbox=dict(boxstyle="round,pad=0.2", fc="black", alpha=0.7))
            
            plt.axis('off')
            plt.tight_layout(pad=0)
            plt.savefig(jpeg_path, bbox_inches='tight', pad_inches=0, dpi=300)
            plt.close()
            
            print(f"Converted {fits_file} to {jpeg_path} with OBJECT: {object_name}")
            return jpeg_path
            
    except Exception as e:
        print(f"Error converting {fits_file}: {str(e)}")
        return None

recent = get_recent_image()
if recent:
    convert_fits_to_jpeg(recent, 'latest-fits.jpg', '/tmp', 'grey')
    subprocess.run(['scp', '/tmp/latest-fits.jpg','dokeeffe@52-8.xyz:/var/www/html/images/.'])
else:
    print('no recent image')
