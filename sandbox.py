import sys
from astropy.io import fits

# --- Replace this path with your actual FITS/FTS file ---
file_path = r"Z:\Infra_Red_Imaging_Station\Tube_Fin_Flow_Tests\IRIS-TF-084\IRIS-TF-084.fts"

# --- Read and print header ---
with fits.open(file_path) as hdul:
    print("\n=== FITS File Structure ===")
    hdul.info()

    print("\n=== Primary Header ===")
    hdul[0].header.totextfile(sys.stdout)
