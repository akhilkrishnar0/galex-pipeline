"""GALEX product discovery and local file organization; no response maps required."""
from pathlib import Path
import gzip
import re
import shutil

PRODUCT = re.compile(r"^(?P<tile>.+)-(?P<band>fd|nd)-(?P<kind>intbgsub|int|skybg)\.fits(?:\.gz)?$")

def unzip_galex_files(folder):
    folder = Path(folder)
    for source in folder.glob("*.gz"):
        if not PRODUCT.match(source.name):
            continue
        target = source.with_suffix("")
        temporary = target.with_suffix(".fits.part")
        try:
            with gzip.open(source, "rb") as fin, temporary.open("wb") as fout:
                shutil.copyfileobj(fin, fout)
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)

def organize_fits(folder):
    folder = Path(folder)
    for band in ("FUV", "NUV"):
        for kind in ("int", "skybg", "intbgsub"):
            (folder / band / kind).mkdir(parents=True, exist_ok=True)
    for source in folder.glob("*.fits"):
        match = PRODUCT.match(source.name)
        if match:
            band = "FUV" if match["band"] == "fd" else "NUV"
            source.replace(folder / band / match["kind"] / source.name)

def image_pairs(folder, band):
    """Return existing intensity images, without requiring matching response files."""
    return sorted((Path(folder) / band / "int").glob("*-int.fits"))
