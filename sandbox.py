import os
import sys
import pandas as pd
from astropy.io import fits

# --- CONFIG ---
base_dir = r"Z:\Infra_Red_Imaging_Station\Tube_Fin_Flow_Tests"
metadata_file = os.path.join(base_dir, "fits_metadata.csv")

# --- Load metadata ---
if metadata_file.lower().endswith(".csv"):
    df = pd.read_csv(metadata_file)
else:
    df = pd.read_excel(metadata_file)

# Normalize column names
df.columns = [c.strip() for c in df.columns]

# --- Loop through each experiment ---
for _, row in df.iterrows():
    experiment = str(row["Experiment"]).strip()
    folder_path = os.path.join(base_dir, experiment)

    if not os.path.isdir(folder_path):
        print(f"[SKIP] Folder not found: {folder_path}")
        continue

    # Find a .fts or .fits file
    fits_file = next((f for f in os.listdir(folder_path) if f.lower().endswith((".fts", ".fits"))), None)
    if not fits_file:
        print(f"[SKIP] No FITS file found in {folder_path}")
        continue

    file_path = os.path.join(folder_path, fits_file)

    # --- Extract metadata values ---
    metadata = {
        "INLET_T": float(row["Inlet_Temp"]),
        "FLOWRATE": float(row["Flow_Rate"]),
        "GRAPHITE": float(row["Graphite"]),
        "RUNTIME": float(row["Runtime"]),
    }

    # --- Update FITS file header ---
    try:
        with fits.open(file_path, mode="update", ignore_missing_end=True) as hdul:
            hdr = hdul[0].header

            for key, val in metadata.items():
                hdr[key] = val

            hdul.flush()

        print(f"[UPDATED] {experiment}: {fits_file}")

    except Exception as e:
        print(f"[ERROR] Failed to update {file_path}: {e}")

# --- Optional: print one header as confirmation ---
print("\n--- Sample header check ---\n")
sample_exp = df.iloc[0]["Experiment"]
sample_file = os.path.join(base_dir, sample_exp, f"{sample_exp}.fts")

with fits.open(sample_file) as hdul:
    hdul[0].header.totextfile(sys.stdout)
