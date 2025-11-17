from pathlib import Path
from astropy.io import fits
from reproject import reproject_interp
import numpy as np


def stack_band(crop_folder: Path, band: str):
    files = sorted((crop_folder / band).glob("*.fits"))
    if not files:
        print(f"No {band} cropped files")
        return

    ref_header = fits.getheader(files[0])
    ref_shape = fits.getdata(files[0]).shape

    weighted = np.zeros(ref_shape)
    wsum = np.zeros(ref_shape)
    total = 0.0

    for f in files:
        data = fits.getdata(f)
        hdr = fits.getheader(f)
        t = hdr.get("EXPTIME", 1)
        repro, _ = reproject_interp((data, hdr), ref_header)

        mask = np.isfinite(repro)
        weighted[mask] += repro[mask] * t
        wsum[mask] += t
        total += t

    out = weighted / np.where(wsum == 0, 1, wsum)
    ref_header["NCOMBINE"] = len(files)
    ref_header["TOTEXPT"] = total

    outname = crop_folder / f"{band}_stacked.fits"
    fits.writeto(outname, out, ref_header, overwrite=True)

    print(f"Saved stacked {band}: {outname}")

