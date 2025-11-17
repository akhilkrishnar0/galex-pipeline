from pathlib import Path
from astropy.io import fits
from astropy.visualization import simple_norm
from astropy.wcs import WCS
import matplotlib.pyplot as plt


def plot_fuv_nuv(galaxy_name, base_folder="downloaded_galex", output_folder="galex_plots"):
    """
    Create a 2–column FUV / NUV stacked image plot for a galaxy.

    Parameters
    ----------
    galaxy_name : str
        Galaxy name (folder name).
    base_folder : str or Path
        Base directory where downloaded_galex/<galaxy_name> exists.
    output_folder : str or Path
        Folder to save PNG plots.
    """

    base = Path(base_folder)
    gal_folder = base / galaxy_name / "cropped"
    outdir = Path(output_folder)
    outdir.mkdir(exist_ok=True)

    fuv_file = gal_folder / "FUV_stacked.fits"
    nuv_file = gal_folder / "NUV_stacked.fits"

    if not (fuv_file.exists() and nuv_file.exists()):
        print(f"❌ Missing FUV/NUV stacked data for {galaxy_name}")
        return None

    # Load FITS
    fuv_data, fuv_hdr = fits.getdata(fuv_file, header=True)
    nuv_data, nuv_hdr = fits.getdata(nuv_file, header=True)

    fuv_wcs = WCS(fuv_hdr)
    nuv_wcs = WCS(nuv_hdr)

    # Image normalization
    fuv_norm = simple_norm(fuv_data, 'log', percent=99.5)
    nuv_norm = simple_norm(nuv_data, 'log', percent=99.5)

    # Plot
    fig, axs = plt.subplots(
        1, 2, figsize=(12, 6),
        subplot_kw={'projection': fuv_wcs}
    )

    # ---- FUV ----
    axs[0].imshow(fuv_data, origin="lower", cmap="gray", norm=fuv_norm)
    axs[0].set_title(f"{galaxy_name} – FUV")
    axs[0].set_xlabel("RA")
    axs[0].set_ylabel("DEC")

    # ---- NUV ----
    axs[1].remove()
    ax2 = fig.add_subplot(1, 2, 2, projection=nuv_wcs)
    ax2.imshow(nuv_data, origin="lower", cmap="gray", norm=nuv_norm)
    ax2.set_title(f"{galaxy_name} – NUV")
    ax2.set_xlabel("RA")
    ax2.set_ylabel("DEC")

    plt.tight_layout()

    outfile = outdir / f"{galaxy_name}_FUV_NUV.png"
    plt.savefig(outfile, dpi=200)
    plt.close()

    print(f"✔ Saved {outfile}")
    return outfile

