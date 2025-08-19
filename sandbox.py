from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt

# Replace with your file path
file_path = "L:\Infra_Red_Imaging_Station\Tube_Fin_Flow_Tests\IRIS-TF-044\IRIS-TF-044.fts"

with fits.open(file_path, memmap=True) as hdul:
    data = hdul[0].data  # still on disk
    print("Full shape:", data.shape)

    # Top-left pixel of the last frame (row=0, col=0)
    value = data[-1, 0, 0]   # [frame, row, col]
    print("Top-left pixel value of last frame:", repr(value))