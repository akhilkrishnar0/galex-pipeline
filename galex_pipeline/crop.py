"""Crop GALEX intensity images without response maps."""
from pathlib import Path
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy.nddata.utils import Cutout2D, NoOverlapError
from .io_utils import image_pairs

def crop_band(base_folder, band, ra, dec, crop_size):
    folder = Path(base_folder)
    output = folder / "cropped" / band
    output.mkdir(parents=True, exist_ok=True)
    paths = []
    position = SkyCoord(ra, dec, unit="deg")
    for intensity in image_pairs(folder, band):
        data, header = fits.getdata(intensity, header=True)
        if data.ndim != 2:
            print(f"Skipping non-2D image: {intensity.name}")
            continue
        try:
            cut = Cutout2D(np.asarray(data, dtype=float), position, crop_size,
                           wcs=WCS(header).celestial, mode="partial", fill_value=np.nan)
        except NoOverlapError:
            print(f"No overlap: {intensity.name}")
            continue
        out_header = header.copy()
        # Reconstruct the FITS header with the updated celestial WCS.
        for key in WCS(header).to_header(relax=True):
            if key in out_header:
                del out_header[key]
        out_header.update(cut.wcs.to_header(relax=True))
        out_header["NAXIS"] = 2
        out_header["NAXIS1"] = cut.data.shape[1]
        out_header["NAXIS2"] = cut.data.shape[0]
        ipath = output / intensity.name.replace(".fits", "_crop.fits")
        fits.writeto(ipath, cut.data, out_header, overwrite=True)
        paths.append(ipath)
    return paths
