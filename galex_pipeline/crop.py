from pathlib import Path
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy.nddata.utils import Cutout2D
import numpy as np


def crop_band(base_folder: Path, band: str, ra: float, dec: float, crop_size):
    band_folder = base_folder / band / "int"
    out_folder = base_folder / "cropped" / band
    out_folder.mkdir(parents=True, exist_ok=True)

    fits_files = sorted(band_folder.glob("*.fits"))
    if not fits_files:
        print(f"❌ No images for {band}")
        return

    for f in fits_files:
        with fits.open(f) as hdul:
            data = hdul[0].data
            header = hdul[0].header
            wcs = WCS(header)

        position = SkyCoord(ra=ra, dec=dec, unit="deg")

        try:
            cutout = Cutout2D(data, position, crop_size, wcs=wcs, mode="trim")
        except:
            print(f"❌ Could not crop {f.name}")
            continue

        new_header = header.copy()
        new_header.update(cutout.wcs.to_header())

        outname = out_folder / f.name.replace(".fits", "_crop.fits")
        fits.writeto(outname, cutout.data, new_header, overwrite=True)
        print(f"Cropped → {outname.name}")

