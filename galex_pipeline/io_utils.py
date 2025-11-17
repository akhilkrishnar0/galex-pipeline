from pathlib import Path
import gzip, shutil


def unzip_galex_files(folder: Path):
    for gz_file in folder.glob("*.gz"):
        output = gz_file.with_suffix("")
        with gzip.open(gz_file, "rb") as f_in:
            with open(output, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"Unzipped: {gz_file.name}")


def organize_fits(folder: Path):
    for band in ["FUV", "NUV"]:
        for dtype in ["int", "skybg", "intbgsub"]:
            (folder / band / dtype).mkdir(parents=True, exist_ok=True)

    for fits_file in folder.glob("*.fits"):
        name = fits_file.name.lower()

        if "-fd-" in name:
            band = "FUV"
        elif "-nd-" in name:
            band = "NUV"
        else:
            continue

        if "intbgsub" in name:
            dtype = "intbgsub"
        elif "skybg" in name:
            dtype = "skybg"
        elif "int" in name:
            dtype = "int"
        else:
            continue

        dest = folder / band / dtype / fits_file.name
        shutil.move(str(fits_file), dest)
        print(f"Moved {fits_file.name} → {band}/{dtype}")

