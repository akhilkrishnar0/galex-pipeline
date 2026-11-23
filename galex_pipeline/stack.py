"""Reproject and average valid GALEX intensity pixels without rrhr weighting."""
from pathlib import Path
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_area
from reproject import reproject_interp

def stack_band(crop_folder, band, pairs=None):
    folder = Path(crop_folder)
    paths = list(pairs) if pairs is not None else sorted((folder / band).glob("*-int_crop.fits"))
    if not paths:
        print(f"No overlapping {band} intensity images")
        return None
    ref = fits.getheader(paths[0])
    shape = fits.getdata(paths[0]).shape
    numerator = np.zeros(shape, dtype=float)
    weight = np.zeros(shape, dtype=float)
    coverage = np.zeros(shape, dtype=np.int32)
    nominal = []
    ref_area = proj_plane_pixel_area(WCS(ref).celestial)
    for ipath in paths:
        data, header = fits.getdata(ipath, header=True)
        area = proj_plane_pixel_area(WCS(header).celestial)
        if not np.isclose(area, ref_area, rtol=1e-5, atol=0):
            raise ValueError("Pixel areas differ; explicit surface-brightness conversion required")
        valid = np.isfinite(data)
        values = np.where(valid, data, 0.0)
        counts = valid.astype(float)
        n, footprint = reproject_interp((values, header), ref, shape_out=shape)
        w, _ = reproject_interp((counts, header), ref, shape_out=shape)
        good = (footprint > 0) & np.isfinite(n) & np.isfinite(w) & (w > 0)
        numerator[good] += n[good]
        weight[good] += w[good]
        coverage[good] += 1
        exp = header.get("EXPTIME")
        if exp is not None and np.isfinite(exp):
            nominal.append(float(exp))
    if not np.any(weight > 0):
        raise ValueError(f"No valid overlapping pixels for {band}")
    out = np.full(shape, np.nan)
    np.divide(numerator, weight, out=out, where=weight > 0)
    header = WCS(ref).celestial.to_header()
    header["NCOMBINE"] = len(paths)
    header["WGHTTYPE"] = "UNIFORM"
    header["PIPEVER"] = "0.3.0"
    if len(nominal) == len(paths):
        header["TOTEXPT"] = (sum(nominal), "Nominal summed EXPTIME, not spatial exposure")
    header.add_history("Valid intensity images reprojected and averaged; no rrhr maps used.")
    header.add_history("The coadd is not exposure-weighted; uncovered pixels are NaN.")
    outputs = {}
    for suffix, array, unit in (("stacked", out, ref.get("BUNIT", "count/s/pixel")),
                                ("coverage", coverage, "1")):
        h = header.copy()
        h["BUNIT"] = unit
        path = folder / f"{band}_{suffix}.fits"
        fits.writeto(path, array, h, overwrite=True)
        outputs[suffix] = path
    # Prevent an old response-weighted product from being mistaken for a new one.
    (folder / f"{band}_rrhr.fits").unlink(missing_ok=True)
    return outputs
