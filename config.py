#-----------------------------------------
# Acceptable File Names
#-----------------------------------------

REQUIRED_FILES = {
    'Heat Map': ['Heat_Map_Final_Frame.csv', 'Ti_Fin_Flir.csv'],
    'Chamfered Side, Flir': ['Chamfered_Side_TC_Flir.txt'],
    'Filleted Side, Flir': ['Filleted_Side_TC_Flir.txt'],
    'External Sensors, Arduino': ['sensors.txt'],
    'Simulation Data': ['IRIS-ANSYS']
}

#-----------------------------------------
# Fin Properties
#-----------------------------------------

TC_F_VLOC = 27.65        # Vertical location of the filleted edge thermocouple from the top edge in mm
TC_F_HLOC = 16.77        # Horizontal location of the filleted edge thermocouple from the right edge in mm
TC_C_VLOC = 28.47       # Vertical location of the chamfered edge thermocouple from the bottom edge in mm
TC_C_HLOC = 16.71       # Horizontal location of the chamfered edge thermocouple from the right edge in mm
FIN_WIDTH = 34.02               # Width of the fin in mm
FIN_HEIGHT = 90.28              # Height of the fin in mm

#-----------------------------------------
# Calibration Properties
#-----------------------------------------

EDGE_SENSITIVITY = 125  # Pixel window near top/bottom edges

#-----------------------------------------
# Arduino Connection Properties
#-----------------------------------------

SERIAL_PORT = 'COM3'  # Default port for Arduino connection
BAUD_RATE = 9600  # Baud rate for serial communication

#-----------------------------------------
# Figure & Font Formatting (for Publication)
#-----------------------------------------

HEATMAP_FIGURE_SIZE = (8, 3)      # inches, optimized for heat map
PLOT_FIGURE_SIZE = (8, 6)            # inches, standard for single-column figures
FIGURE_DPI = 300                # dots per inch, 300+ recommended for print

PLOT_FONT_CONFIG = {
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial'],
    'font.size': 20,            # Base font size for most text
    'axes.labelsize': 20,       # Axis labels (e.g., "Temperature (°C)")
    'axes.titlesize': 20,       # Title size (if used)
    'xtick.labelsize': 20,       # X-axis tick labels
    'ytick.labelsize': 20,       # Y-axis tick labels
    'legend.fontsize': 16,       # Legend text
    'figure.titlesize': 20,     # Figure title (if used)
}

HEATMAP_FONT_CONFIG = {
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial'],
    'font.size': 16,            # Base font size for most text
    'axes.labelsize': 16,       # Axis labels (e.g., "Temperature (°C)")
    'axes.titlesize': 16,       # Title size (if used)
    'xtick.labelsize': 16,       # X-axis tick labels
    'ytick.labelsize': 16,       # Y-axis tick labels
    'legend.fontsize': 16,       # Legend text
    'figure.titlesize': 16,     # Figure title (if used)
}

HEATMAP_SCALE = 2.5  # Scale factor for heat map resolution
LINEAR_PROFILE_SCALE = 2.5  # Scale factor for linear profile resolution
COMBINED_LINEAR_PROFILE_SCALE = 2.5  # Scale factor for combined linear profile resolution
TEMPORAL_PLOT_SCALE = 1  # Scale factor for temporal plots

COMBINED_PLOT_GRAPHITE_CMAP = 'bwr'  # Colormap for combined plots
COMBINED_PLOT_INLET_TEMP_CMAP = 'rainbow'  # Colormap for combined plots
COMBINED_PLOT_FLOW_RATE_CMAP = 'viridis'  # Colormap for combined plots
HEATMAP_CMAP = 'jet'    # Colormap for heat maps

COMPARISON_TO_USE = 2 # 0 for graphite comparison, 1 for inlet temperature comparison, 2 for flow rate comparison

#-----------------------------------------
# Inverse Thermal Conductivity Fit
#-----------------------------------------

INVERSE_AMBIENT_TEMP_C = 21.2
INVERSE_FIN_THICKNESS_M = 0.001
INVERSE_PROFILE_LENGTH_M = 0.04
INVERSE_AIR_CONV_COEFF_W_M2K = 12
INVERSE_INITIAL_M = 80
INVERSE_BOUNDARY_MODE = 'flux'  # 'flux' or 'temperature'
INVERSE_PROFILE_SIDE = 'chamfered'  # 'chamfered'/'right' or 'filleted'/'left'
INVERSE_PROFILE_PIXEL_LENGTH = 200
INVERSE_PROFILE_HOT_BAND_FRACTION = 0.95

# Python 0-based pixel indices. These defaults reproduce the MATLAB Ti fitting
# workflow (MATLAB row 120, columns 348:548). Set all three to None to infer a
# tube-wall-to-edge profile from the selected experiment.
INVERSE_PROFILE_ROW_PIXEL = 119
INVERSE_PROFILE_START_PIXEL = 347
INVERSE_PROFILE_END_PIXEL = 547
