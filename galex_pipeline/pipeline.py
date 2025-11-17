from pathlib import Path
from astropy.coordinates import SkyCoord
from astropy import units as u

from .io_utils import unzip_galex_files, organize_fits
from .crop import crop_band
from .stack import stack_band


def process_galaxy(gname: str, root="downloaded_galex", crop_size=800*u.arcsec):

    folder = Path(root) / gname
    folder.mkdir(exist_ok=True)

    print(f"\n=== Processing {gname} ===")

    pos = SkyCoord.from_name(gname)
    ra, dec = pos.ra.deg, pos.dec.deg

    unzip_galex_files(folder)
    organize_fits(folder)

    crop_band(folder, "FUV", ra, dec, crop_size)
    crop_band(folder, "NUV", ra, dec, crop_size)

    cropped = folder / "cropped"
    stack_band(cropped, "FUV")
    stack_band(cropped, "NUV")


def process_many(galaxy_list, root="downloaded_galex", crop_size=800*u.arcsec):
    for g in galaxy_list:
        process_galaxy(g, root, crop_size)
    print("\nAll galaxies processed!")

