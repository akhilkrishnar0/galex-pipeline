# GALEX Pipeline

A clean, modular Python package to automate:

- Unzipping GALEX tiles
- Organizing FITS files into FUV/NUV
- Cropping around galaxy center (RA/DEC)
- Stacking exposures using exposure-weighted reprojecting
- Producing final FUV/NUV stacked images

---

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/galex-pipeline.git
cd galex-pipeline

Install the package:

pip install -e .

Usage Example (Jupyter Notebook or Python)
import galex_pipeline as gp

gp.process_galaxy("NGC6902")


Process multiple galaxies:

gp.process_many(["NGC6902", "NGC1316"])


Your GALEX data must be inside:

downloaded_galex/NGC6902/*.gz
downloaded_galex/NGC1316/*.gz

Project Structure
galex_pipeline/
    io_utils.py     # unzip + organize
    crop.py         # cropping code
    stack.py        # stacking code
    pipeline.py     # orchestration

License

MIT License


---

# 📦 Package Source Files

---

## **4️⃣ galex_pipeline/__init__.py**

```python
from .pipeline import process_galaxy, process_many
