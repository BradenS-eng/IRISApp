#-----------------------------------------
# Acceptable File Names
#-----------------------------------------

REQUIRED_FILES = {
    'Heat Map': ['Heat_Map_Final_Frame.csv', 'Ti_Fin_Flir.csv'],
    'Chamfered Side, Flir': ['Chamfered_Side_TC_Flir.txt'],
    'Filleted Side, Flir': ['Filleted_Side_TC_Flir.txt'],
    'External Sensors, Arduino': ['sensors.txt']
}

#-----------------------------------------
# Fin Properties
#-----------------------------------------

TC_F_VLOC = 27.65        # Vertical location of the filleted edge thermocouple from the top edge in mm
TC_F_HLOC = 16.77        # Horizontal location of the filleted edge thermocouple from the left edge in mm
TC_C_VLOC = 28.47       # Vertical location of the chamfered edge thermocouple from the bottom edge in mm
TC_C_HLOC = 16.71       # Horizontal location of the chamfered edge thermocouple from the top left edge in mm
FIN_WIDTH = 34.02               # Width of the fin in mm
FIN_HEIGHT = 90.28              # Height of the fin in mm

#-----------------------------------------
# Calibration Properties
#-----------------------------------------

EDGE_SENSITIVITY = 80  # Pixel window near top/bottom edges
FIGURE_SIZE = (8, 6)