"""Process GALEX intensity images without rrhr maps."""
from pathlib import Path
from astropy.coordinates import SkyCoord
from astropy import units as u
from .io_utils import unzip_galex_files, organize_fits, image_pairs
from .crop import crop_band
from .stack import stack_band

def process_galaxy(gname, root="downloaded_galex", crop_size=800*u.arcsec):
    folder = Path(root) / gname.replace(" ", "")
    if not folder.is_dir():
        raise FileNotFoundError(f"Download data first: {folder}")
    pos = SkyCoord.from_name(gname)
    unzip_galex_files(folder)
    organize_fits(folder)
    result = {}
    for band in ("FUV", "NUV"):
        if not image_pairs(folder, band):
            raise FileNotFoundError(f"No {band} intensity images in {folder}")
        paths = crop_band(folder, band, pos.ra.deg, pos.dec.deg, crop_size)
        if not paths:
            raise ValueError(f"No overlapping {band} images for {gname}")
        result[band] = stack_band(folder / "cropped", band, pairs=paths)
    return result

def process_many(galaxy_list, root="downloaded_galex", crop_size=800*u.arcsec):
    return {g: process_galaxy(g, root, crop_size) for g in galaxy_list}
