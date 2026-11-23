"""Download GALEX science products without requiring rrhr maps."""
from pathlib import Path
import json
import time
from astropy.coordinates import SkyCoord
from astropy import units as u
from astroquery.mast import Observations
from .io_utils import PRODUCT, unzip_galex_files, organize_fits, image_pairs

def download_galex(galaxy, root="downloaded_galex", radius=0.1*u.deg, retries=3):
    if retries < 1:
        raise ValueError("retries must be at least 1")
    folder = Path(root) / galaxy.replace(" ", "")
    folder.mkdir(parents=True, exist_ok=True)
    pos = SkyCoord.from_name(galaxy)
    if not isinstance(radius, u.Quantity):
        radius = radius * u.deg
    obs = Observations.query_region(pos, radius=radius)
    obs = obs[obs["obs_collection"] == "GALEX"]
    if not len(obs):
        raise ValueError(f"No GALEX observations for {galaxy}")
    products = Observations.get_product_list(obs)
    selected = {}
    for row in products:
        name = str(row["productFilename"])
        if PRODUCT.match(name):
            selected[str(row["dataURI"])] = name
    if not any("-int.fits" in n for n in selected.values()):
        raise ValueError(f"No GALEX intensity products for {galaxy}")
    records = []
    for uri, name in selected.items():
        match = PRODUCT.match(name)
        band = "FUV" if match["band"] == "fd" else "NUV"
        plain = name.removesuffix(".gz")
        candidates = (folder / plain, folder / name,
                      folder / band / match["kind"] / plain)
        existing = next((p for p in candidates if p.is_file() and p.stat().st_size > 0), None)
        if existing is None:
            target = folder / name
            temporary = folder / (name + ".part")
            for attempt in range(retries):
                try:
                    result = Observations.download_file(uri, local_path=str(temporary), cache=False)
                    if result[0] != "COMPLETE" or not temporary.is_file() or temporary.stat().st_size == 0:
                        raise OSError(f"MAST download failed: {result}")
                    temporary.replace(target)
                    break
                except Exception:
                    temporary.unlink(missing_ok=True)
                    if attempt + 1 == retries:
                        raise
                    time.sleep(10)
        records.append({"uri": uri, "filename": name})
    unzip_galex_files(folder)
    organize_fits(folder)
    if not any(image_pairs(folder, b) for b in ("FUV", "NUV")):
        raise ValueError(f"No intensity images available after download for {galaxy}")
    (folder / "download_manifest.json").write_text(json.dumps(records, indent=2) + "\n")
    return folder
