# ========================== Imports & Config ==========================
import os
import math
import config
import statistics
import numpy as np
import pandas as pd
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from scipy.ndimage import gaussian_filter1d
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

# Global App Config
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')  # Infrared-friendly color theme

# ========================== Main Application Class ==========================
class IRISApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('IRIS - Infrared Imaging Suite')
        self.geometry('1400x800')

        self.current_tabs = set()  # Track created tabs
        self.heat_map_data = {}
        self.heat_map_data_filenames = {}
        self.sensors_data = {}
        self.sensors_data_filenames = {}
        self.flir_chamfered_data = {}
        self.flir_chamfered_data_filenames = {}
        self.flir_filleted_data = {}
        self.flir_filleted_data_filenames = {}
        self.simulation_data = {}
        self.simulation_data_filesnames = {}
        self.left_edges = {}
        self.right_edges = {}
        self.top_edges = {}
        self.bottom_edges = {}
        self.midline = {}
        self.c_tc_location = {}
        self.f_tc_location = {}
        self.is_vertical = {}
        self.averages = {}

        self.current_plot_canvas = {}

        self.create_workspace()

        self.protocol('WM_DELETE_WINDOW', self.on_closing)

    def on_closing(self):
        try:
            self.quit()
        except:
            pass

# ========================== Building the Workspace ==========================
    def create_workspace(self):

    # Top Frame for Directory Selector
        directory_frame = ctk.CTkFrame(self)
        directory_frame.pack(side='top', fill='x', padx=10, pady=5)
        self.build_directory_selector(directory_frame)
        
    # Left Frame for Available Experiments and Workspace
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.pack(side='left', fill='y', padx=5, pady=5)
        self.build_available_experiments_box(self.left_frame)
        self.build_selected_experiments_box(self.left_frame)
        self.build_status_box(self.left_frame)

    # Center Frame for Visualization and Plotting
        self.center_frame = ctk.CTkFrame(self)
        self.center_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        self.build_center_box(self.center_frame)

    # Plot Box
        self.plot_box_frame = ctk.CTkFrame(self)
        self.plot_box_frame.pack(side='top', fill='x', anchor='n', padx=5, pady=5)
        self.plot_box_label = ctk.CTkLabel(self.plot_box_frame, text='Plot Selector', width=225, font=(None, 20))
        self.plot_box_label.pack(anchor='w')
        self.build_plot_box(self.plot_box_frame)

    # System Dashboard
        self.system_dashboard_frame = ctk.CTkFrame(self)
        self.system_dashboard_frame.pack(side='top', fill='x', anchor='n', padx=5, pady=5)
        self.system_dashboard_label = ctk.CTkLabel(self.system_dashboard_frame, text='System Dashboard', width=225, font=(None, 20))
        self.system_dashboard_label.pack(anchor='n')
        self.build_information_frame(self.system_dashboard_frame)

# ============================ Building Workspace Components ==========================
    def build_directory_selector(self, parent):
        self.dir_entry = ctk.CTkEntry(parent, placeholder_text='Select a directory with experiment folders')
        self.dir_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))

        browse_button = ctk.CTkButton(parent, text='Browse', command=self.browse_directory)
        browse_button.pack(side='left', padx=5)

        reset_button = ctk.CTkButton(parent, text='Reset', command=self.reset_workspace)
        reset_button.pack(side='left')

    def build_available_experiments_box(self, parent):
        self.available_experiments = ctk.CTkLabel(parent, text='Available Experiments', width=225, font=(None, 20))
        self.available_experiments.pack(anchor='n')
        self.available_experiments_listbox = ctk.CTkScrollableFrame(parent, height=150)
        self.available_experiments_listbox.pack(fill='x', expand='false', pady=(0, 10))

    def build_selected_experiments_box(self, parent):
        self.selected_experiments_label = ctk.CTkLabel(parent, text='Selected Experiments', width=225, font=(None, 20))
        self.selected_experiments_label.pack(anchor='n')
        self.selected_experiments_listbox = ctk.CTkScrollableFrame(parent, height=150)
        self.selected_experiments_listbox.pack(fill='x', expand='false', pady=(0, 10))

    def build_center_box(self, parent):
        self.experiments_tabs = ctk.CTkTabview(parent, command=self.on_tab_change)
        self.experiments_tabs.pack(fill='both', expand=True)
        self.experiments_tabs.add('Combined Plot')

    def build_status_box(self, parent):
        self.status_label = ctk.CTkLabel(parent, text='File Status', width=225, font=(None, 20))
        self.status_label.pack(anchor='n')
        
        self.status_frame = ctk.CTkScrollableFrame(parent)
        self.status_frame.pack(side='top', fill='x', anchor='n', pady=(0,10))

        self.heatmap_label = ctk.CTkLabel(self.status_frame, text='Heatmap File:')
        self.heatmap_label.pack(anchor='w')

        self.heatmap_file_label = ctk.CTkEntry(self.status_frame, height=25, justify='right')
        self.heatmap_file_label.pack(fill='x', pady=(0, 5), padx=5)
        self.heatmap_file_label.insert(0, 'No file loaded')
        self.heatmap_file_label.configure(state='disabled')

        self.sensors_label = ctk.CTkLabel(self.status_frame, text='Sensors File:')
        self.sensors_label.pack(anchor='w')

        self.sensors_file_label = ctk.CTkEntry(self.status_frame, height=25, justify='right')
        self.sensors_file_label.pack(fill='x', pady=(0, 5), padx=5)
        self.sensors_file_label.insert(0, 'No file loaded')
        self.sensors_file_label.configure(state='disabled')

        self.chamfered_label = ctk.CTkLabel(self.status_frame, text='Chamfered Flir Temp File:')
        self.chamfered_label.pack(anchor='w')

        self.chamfered_file_label = ctk.CTkEntry(self.status_frame, height=25, justify='right')
        self.chamfered_file_label.pack(fill='x', pady=(0, 5), padx=5)
        self.chamfered_file_label.insert(0, 'No file loaded')
        self.chamfered_file_label.configure(state='disabled')

        self.filleted_label = ctk.CTkLabel(self.status_frame, text='Filleted Flir Temp File:')
        self.filleted_label.pack(anchor='w')

        self.filleted_file_label = ctk.CTkEntry(self.status_frame, height=25, justify='right')
        self.filleted_file_label.pack(fill='x', pady=(0, 5), padx=5)
        self.filleted_file_label.insert(0, 'No file loaded')
        self.filleted_file_label.configure(state='disabled')

        self.simulation_label = ctk.CTkLabel(self.status_frame, text='Simulation File:')
        self.simulation_label.pack(anchor='w')

        self.simulation_file_label = ctk.CTkEntry(self.status_frame, height=25, justify='right')
        self.simulation_file_label.pack(fill='x', pady=(0, 5), padx=5)
        self.simulation_file_label.insert(0, 'No file loaded')
        self.simulation_file_label.configure(state='disabled')

    def build_plot_box(self, parent):
        self.plot_heatmap_frame = ctk.CTkFrame(parent)
        self.plot_heatmap_frame.pack(anchor='w', fill='x', expand=True, padx=5, pady=5)

        self.plot_heatmap_btn = ctk.CTkButton(self.plot_heatmap_frame, text='Plot Heat Map', command=self.plot_heat_map)
        self.plot_heatmap_btn.pack(fill='x', expand=True, padx=5, pady=5)

        self.fin_box_checkbox = ctk.CTkCheckBox(self.plot_heatmap_frame, text='Show Fin Box', command=self.plot_heat_map)
        self.fin_box_checkbox.pack(anchor='w', padx=5, pady=5)
        self.fin_box_checkbox.select()

        self.midline_checkbox = ctk.CTkCheckBox(self.plot_heatmap_frame, text='Show Midline', command=self.plot_heat_map)
        self.midline_checkbox.pack(anchor='w', padx=5, pady=5)
        self.midline_checkbox.select()

        self.thermocouples_checkbox = ctk.CTkCheckBox(self.plot_heatmap_frame, text='Show Thermocouple Locations', command=self.plot_heat_map)
        self.thermocouples_checkbox.pack(anchor='w', padx=5, pady=5)
        self.thermocouples_checkbox.select()

        self.linear_plot_frame = ctk.CTkFrame(parent)
        self.linear_plot_frame.pack(anchor='w', fill='x', expand=True, padx=5, pady=5)
        
        self.plot_linear_profile_btn = ctk.CTkButton(self.linear_plot_frame, text='Plot Linear Temperature Profile', command=self.plot_linear_profile)
        self.plot_linear_profile_btn.pack(fill='x', expand=True, padx=5, pady=5)

        self.simulation_checkbox = ctk.CTkCheckBox(self.linear_plot_frame, text='Include Simulation Results', command=self.plot_linear_profile)
        self.simulation_checkbox.pack(anchor='w', padx=5, pady=5)
        self.simulation_checkbox.select()

        self.plot_temporal_data_frame = ctk.CTkFrame(parent)
        self.plot_temporal_data_frame.pack(anchor='w', fill='x', expand=True, padx=5, pady=5)

        self.plot_temporal_btn = ctk.CTkButton(self.plot_temporal_data_frame, text='Plot Temporal Data', command=self.plot_temporal_data)
        self.plot_temporal_btn.pack(anchor='w', fill='x', expand=True, padx=5, pady=5)

        self.plot_thermocouple_temps = ctk.CTkCheckBox(self.plot_temporal_data_frame, text='Show Thermocouple Temperatures', command=self.plot_temporal_data)
        self.plot_thermocouple_temps.pack(anchor='w', padx=5, pady=5)
        self.plot_thermocouple_temps.select()

        self.plot_flir_temps = ctk.CTkCheckBox(self.plot_temporal_data_frame, text='Show Flir Temperatures', command=self.plot_temporal_data)
        self.plot_flir_temps.pack(anchor='w', padx=5, pady=5)
        self.plot_flir_temps.select()

        self.plot_inlet_temp = ctk.CTkCheckBox(self.plot_temporal_data_frame, text='Inlet Temperature', command=self.plot_temporal_data)
        self.plot_inlet_temp.pack(anchor='w', padx=5, pady=5)
        self.plot_inlet_temp.select()

        self.plot_flow_rate = ctk.CTkCheckBox(self.plot_temporal_data_frame, text='Show Flow Rates', command=self.plot_temporal_data)
        self.plot_flow_rate.pack(anchor='w', padx=5, pady=5)
        self.plot_flow_rate.select()

    def build_information_frame(self, parent):
        self.information_frame = ctk.CTkFrame(parent)
        self.information_frame.pack(side='top', fill='x', anchor='n', padx=5, pady=5)

        self.information_label = ctk.CTkLabel(self.information_frame, text='Thermocouples, (→,↓)', width=225, font=(None, 18))
        self.information_label.pack(anchor='w')

        self.chamfered_tc_label = ctk.CTkLabel(self.information_frame, text='Chamfered TC Location')
        self.chamfered_tc_label.pack(anchor='w')

        self.chamfered_tc_location = ctk.CTkEntry(self.information_frame, height=25, justify='right')
        self.chamfered_tc_location.pack(fill='x', pady=(0, 5), padx=5)
        self.chamfered_tc_location.insert(0, 'Select Heatmap')
        self.chamfered_tc_location.configure(state='disabled')

        self.filleted_tc_label = ctk.CTkLabel(self.information_frame, text='Filleted TC Location')
        self.filleted_tc_label.pack(anchor='w')

        self.filleted_tc_location = ctk.CTkEntry(self.information_frame, height=25, justify='right')
        self.filleted_tc_location.pack(fill='x', pady=(0, 5), padx=5)
        self.filleted_tc_location.insert(0, 'Select Heatmap')
        self.filleted_tc_location.configure(state='disabled')

        self.averages_frame = ctk.CTkFrame(parent)
        self.averages_frame.pack(side='top', fill='x', anchor='n', padx=5, pady=5)

        self.averages_label = ctk.CTkLabel(self.averages_frame, text='Averages', width=225, font=(None, 18))
        self.averages_label.grid(row=0, column=0, columnspan=2, sticky='w', padx=5, pady=(0, 10))   

        self.chamfered_ave_label = ctk.CTkLabel(self.averages_frame, text='Ard-C (°C)')
        self.chamfered_ave_label.grid(row=1, column=0, sticky='w', padx=5)

        self.chamfered_ave_box = ctk.CTkEntry(self.averages_frame, height=25, justify='right')
        self.chamfered_ave_box.grid(row=2, column=0, padx=5, pady=(0, 5), sticky='ew')
        self.chamfered_ave_box.insert(0, 'N/A')
        self.chamfered_ave_box.configure(state='disabled')

        self.filleted_ave_label = ctk.CTkLabel(self.averages_frame, text='Ard-F (°C)')
        self.filleted_ave_label.grid(row=1, column=1, sticky='w', padx=5)

        self.filleted_ave_box = ctk.CTkEntry(self.averages_frame, height=25, justify='right')
        self.filleted_ave_box.grid(row=2, column=1, padx=5, pady=(0, 5), sticky='ew')
        self.filleted_ave_box.insert(0, 'N/A')
        self.filleted_ave_box.configure(state='disabled')

        self.averages_frame.grid_columnconfigure(0, weight=1)
        self.averages_frame.grid_columnconfigure(1, weight=1)

        self.chamfered_flir_label = ctk.CTkLabel(self.averages_frame, text='Flir-C (°C)')
        self.chamfered_flir_label.grid(row=3, column=0, sticky='w', padx=5)

        self.chamfered_flir_box = ctk.CTkEntry(self.averages_frame, height=25, justify='right')
        self.chamfered_flir_box.grid(row=4, column=0, padx=5, pady=(0, 5), sticky='ew')
        self.chamfered_flir_box.insert(0, 'N/A')
        self.chamfered_flir_box.configure(state='disabled')

        self.filleted_flir_label = ctk.CTkLabel(self.averages_frame, text='Flir-F (°C)')
        self.filleted_flir_label.grid(row=3, column=1, sticky='w', padx=5)

        self.filleted_flir_box = ctk.CTkEntry(self.averages_frame, height=25, justify='right')
        self.filleted_flir_box.grid(row=4, column=1, padx=5, pady=(0, 5), sticky='ew')
        self.filleted_flir_box.insert(0, 'N/A')
        self.filleted_flir_box.configure(state='disabled')

        self.fluid_temp_label = ctk.CTkLabel(self.averages_frame, text='Fluid Temp. (°C)')
        self.fluid_temp_label.grid(row=5, column=0, sticky='w', padx=5)

        self.fluid_temp_box = ctk.CTkEntry(self.averages_frame, height=25, justify='right')
        self.fluid_temp_box.grid(row=6, column=0, padx=5, pady=(0, 5), sticky='ew')
        self.fluid_temp_box.insert(0, 'N/A')
        self.fluid_temp_box.configure(state='disabled')

        self.flowrate_label = ctk.CTkLabel(self.averages_frame, text='Flow Rate (L/min)')
        self.flowrate_label.grid(row=5, column=1, sticky='w', padx=5)

        self.flowrate_box = ctk.CTkEntry(self.averages_frame, height=25, justify='right')
        self.flowrate_box.grid(row=6, column=1, padx=5, pady=(0, 5), sticky='ew')
        self.flowrate_box.insert(0, 'N/A')
        self.flowrate_box.configure(state='disabled')

        self.averages_frame.grid_columnconfigure(0, weight=1)
        self.averages_frame.grid_columnconfigure(1, weight=1)


# ============================ File Browser Functions ==========================
    def browse_directory(self):
        selected_dir = filedialog.askdirectory()
        if selected_dir:
            self.dir_entry.delete(0, 'end')
            self.dir_entry.insert(0, selected_dir)
            self.populate_available_experiments(selected_dir)

    def populate_available_experiments(self, path):
        for widget in self.available_experiments_listbox.winfo_children():
            widget.destroy()

        for folder in sorted(os.listdir(path)):
            full_path = os.path.join(path, folder)
            if os.path.isdir(full_path):
                btn = ctk.CTkButton(self.available_experiments_listbox, text=folder, command=lambda name=folder: self.add_to_selected_experiments(name))
                btn.pack(fill='x', pady=1)

    def add_to_selected_experiments(self, folder_name):
        if len(self.current_tabs) >= 10:
            return
        
        for widget in self.selected_experiments_listbox.winfo_children():
            if getattr(widget, 'folder_name', None) == folder_name:
                return
            
        for widget in self.available_experiments_listbox.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == folder_name:
                widget.destroy()
                break
        
        if folder_name not in self.current_tabs:
            self.experiments_tabs.add(folder_name)
            self.current_tabs.add(folder_name)

        base_dir = self.dir_entry.get()
        experiment_path = os.path.normpath(os.path.join(base_dir, folder_name))

        self.import_heatmap(experiment_path)
        self.import_sensors(experiment_path)
        self.import_flir_chamfered(experiment_path)
        self.import_flir_filleted(experiment_path)
        self.import_simulation_data(experiment_path)
        self.check_orientation(folder_name)
        self.plate_edge_detection(folder_name)
        self.find_thermocouples(folder_name)
        self.get_averages(folder_name)
        self.plot_combined_linear_profile()

        name_button_frame = ctk.CTkFrame(self.selected_experiments_listbox)
        name_button_frame.folder_name = folder_name
        name_button_frame.pack(fill='x', pady=1)

        filename_label = ctk.CTkLabel(name_button_frame, text=folder_name)
        filename_label.pack(side='left', fill='x', expand=True)

        remove_btn = ctk.CTkButton(name_button_frame, text='X', width=30, command=lambda f=name_button_frame: self.remove_selected_experiments_item(f))
        remove_btn.pack(side='right')

    def reset_workspace(self):
        for widget in self.available_experiments_listbox.winfo_children():
            widget.destroy()
        for widget in self.selected_experiments_listbox.winfo_children():
            widget.destroy()

        tabs_to_remove = [tab for tab in self.current_tabs if tab != 'Combined Plot']
        for tab in tabs_to_remove:
            self.experiments_tabs.delete(tab)

        self.current_tabs.clear()
        self.current_tabs.add('Combined Plot')

        self.heat_map_data.clear()
        self.heat_map_data_filenames.clear()
        self.sensors_data.clear()
        self.sensors_data_filenames.clear()
        self.flir_chamfered_data.clear()
        self.flir_chamfered_data_filenames.clear()
        self.flir_filleted_data.clear()
        self.flir_filleted_data_filenames.clear()
        self.simulation_data.clear()
        self.simulation_data_filesnames.clear()
        self.left_edges.clear()
        self.right_edges.clear()
        self.top_edges.clear()
        self.bottom_edges.clear()
        self.midline.clear()
        self.c_tc_location.clear()
        self.f_tc_location.clear()
        self.is_vertical.clear()
        self.averages.clear()

        self.dir_entry.delete(0, 'end')

        self.on_tab_change()

        combined_tab_frame = self.experiments_tabs.tab('Combined Plot')
        for widget in combined_tab_frame.winfo_children():
            widget.destroy()

        if 'Combined Plot' in self.current_plot_canvas:
            del self.current_plot_canvas['Combined Plot']

    def remove_selected_experiments_item(self, frame):
        folder_name = getattr(frame, 'folder_name', None)
        if folder_name and folder_name in self.current_tabs:
            self.experiments_tabs.delete(folder_name)
            self.current_tabs.remove(folder_name)
            self.on_tab_change()

        frame.destroy()

        self.heat_map_data.pop(folder_name, None)
        self.heat_map_data_filenames.pop(folder_name, None)
        self.sensors_data.pop(folder_name, None)
        self.sensors_data_filenames.pop(folder_name, None)
        self.flir_chamfered_data.pop(folder_name, None)
        self.flir_chamfered_data_filenames.pop(folder_name, None)
        self.flir_filleted_data.pop(folder_name, None)
        self.flir_filleted_data_filenames.pop(folder_name, None)
        self.simulation_data.pop(folder_name, None)
        self.simulation_data_filesnames.pop(folder_name, None)
        self.left_edges.pop(folder_name, None)
        self.right_edges.pop(folder_name, None)
        self.top_edges.pop(folder_name, None)
        self.bottom_edges.pop(folder_name, None)
        self.midline.pop(folder_name, None)
        self.c_tc_location.pop(folder_name, None)
        self.f_tc_location.pop(folder_name, None)
        self.is_vertical.pop(folder_name, None)
        self.averages.pop(folder_name, None)

        self.plot_combined_linear_profile()
        
        available_folders = []
        for widget in self.available_experiments_listbox.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                available_folders.append(widget.cget("text"))
                widget.destroy()  # Clear all buttons to rebuild sorted list

        available_folders.append(folder_name)
        available_folders = sorted(available_folders, key=str.lower)  # case-insensitive sort

        for folder in available_folders:
            btn = ctk.CTkButton(self.available_experiments_listbox,
                                text=folder,
                                command=lambda name=folder: self.add_to_selected_experiments(name))
            btn.pack(fill='x', pady=1)


# ============================ Data Import Functions ==========================
    def import_heatmap(self, folder_path):
        heat_map_file_name = config.REQUIRED_FILES['Heat Map']
        experiment = os.path.basename(folder_path)
        for file in heat_map_file_name:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                try:
                    self.heat_map_data[experiment] = pd.read_csv(file_path, header=None)
                    self.heat_map_data_filenames[experiment] = file
                    break
                except Exception:
                    continue

        else:
            self.heat_map_data[experiment] = 'Heatmap Data File Not Found'
            self.heat_map_data_filenames[experiment] = 'No File Found in Directory'

    def import_sensors(self, folder_path):
        sensors_file_name = config.REQUIRED_FILES['External Sensors, Arduino']
        experiment = os.path.basename(folder_path)
        for file in sensors_file_name:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                try:
                    self.sensors_data[experiment] = pd.read_csv(file_path, sep=',', skiprows=2)
                    self.sensors_data[experiment] = self.sensors_data[experiment].iloc[:-1, :]
                    split_cols = self.sensors_data[experiment][self.sensors_data[experiment].columns[0]].str.replace('->', '', regex=False).str.split(' ', n=1, expand=True)
                    self.sensors_data[experiment]['Absolute_Time'] = split_cols[0]
                    self.sensors_data[experiment]['Elapsed_Time'] = split_cols[1]
                    self.sensors_data[experiment] = self.sensors_data[experiment].drop(columns=self.sensors_data[experiment].columns[0])
                    cols = ['Absolute_Time', 'Elapsed_Time'] + [col for col in self.sensors_data[experiment].columns if col not in ['Absolute_Time', 'Elapsed_Time']]
                    self.sensors_data[experiment] = self.sensors_data[experiment][cols]
                    self.sensors_data[experiment]['Absolute_Time'] = self.sensors_data[experiment]['Absolute_Time'].str.replace(r'(\d{2}:\d{2}:\d{2}):', r'\1.', regex=True)
                    self.sensors_data[experiment]['Absolute_Time'] = pd.to_datetime(self.sensors_data[experiment]['Absolute_Time'],format='%H:%M:%S.%f').apply(lambda t: pd.Timestamp(year=1, month=1, day=1, hour=t.hour, minute=t.minute, second=t.second, microsecond=t.microsecond))
                    self.sensors_data_filenames[experiment] = file
                    break
                except Exception:
                    continue
        else:
            self.sensors_data[experiment] = 'Arduino Sensor Data File Not Found'
            self.sensors_data_filenames[experiment] = 'No File Found in Directory'

    def import_flir_chamfered(self, folder_path):
        chamfered_flir_file_names = config.REQUIRED_FILES['Chamfered Side, Flir']
        experiment = os.path.basename(folder_path)
        for file in chamfered_flir_file_names:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                try:
                    df = pd.read_csv(file_path, sep='\t')
                    df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d %H:%M:%S.%f') - pd.Timedelta(hours=5)
                    df['time'] = df['time'].apply(
                        lambda t: pd.Timestamp(year=1, month=1, day=1, hour=t.hour, minute=t.minute, second=t.second, microsecond=t.microsecond)
                    )
                    self.flir_chamfered_data[experiment] = df
                    self.flir_chamfered_data_filenames[experiment] = file
                    break
                except Exception:
                    continue
        else:
            self.flir_chamfered_data[experiment] = 'Chamfered Flir Data File Not Found'
            self.flir_chamfered_data_filenames[experiment] = 'No File Found in Directory'

    def import_flir_filleted(self, folder_path):
        filleted_flir_file_names = config.REQUIRED_FILES['Filleted Side, Flir']
        experiment = os.path.basename(folder_path)
        for file in filleted_flir_file_names:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                try:
                    df = pd.read_csv(file_path, sep='\t')
                    df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d %H:%M:%S.%f') - pd.Timedelta(hours=5)
                    df['time'] = df['time'].apply(
                        lambda t: pd.Timestamp(year=1, month=1, day=1, hour=t.hour, minute=t.minute, second=t.second, microsecond=t.microsecond)
                    )
                    self.flir_filleted_data[experiment] = df
                    self.flir_filleted_data_filenames[experiment] = file
                    break
                except Exception:
                    continue
        else:
            self.flir_filleted_data[experiment] = 'Filleted Flir Data File Not Found'
            self.flir_filleted_data_filenames[experiment] = 'No File Found in Directory'

    def import_simulation_data(self, folder_path):
        simulation_file_names = config.REQUIRED_FILES['Simulation Data']
        experiment = os.path.basename(folder_path)
        for file in simulation_file_names:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r') as temp_file:
                        df = temp_file.read()          
                                
                    lines = df.strip().split('\n')
                    lines = lines[1:-1]
                    locations = []
                    temperatures = []

                    for line in lines:
                        parts = line.strip().split('\t')
                        if len(parts) == 2:
                            loc = float(parts[0])
                            temp = float(parts[1])
                            locations.append(loc)
                            temperatures.append(temp)

                    df = pd.DataFrame({'Location': locations,
                                        'Temperature': temperatures})
                    

                    min_pos = df['Location'].min()
                    max_pos = df['Location'].max()
                    df['Location'] = ((max_pos - df['Location']) / (max_pos - min_pos)) * config.FIN_HEIGHT
                    
                    df['Temperature'] = df['Temperature']-273.15
                    df = df.iloc[::-1].reset_index(drop=True)
                    
                    self.simulation_data[experiment] = df
                    self.simulation_data_filesnames[experiment] = file
                    break
                except Exception:
                    continue
        else:
            self.simulation_data[experiment] = 'Simulation Data File Not Found'
            self.simulation_data_filesnames[experiment] = 'No File Found in Directory'

    def check_orientation(self, folder_name):
        if folder_name not in self.heat_map_data or isinstance(self.heat_map_data[folder_name], str):
                return

        data = self.heat_map_data[folder_name]
        top_box = data.iloc[0:7, :].values
        bottom_box = data.iloc[-7:, :].values
        left_box = data.iloc[:, 0:7].values
        right_box = data.iloc[:, -7:].values

        def orientation_score(box):
            box = np.asarray(box)

            grad_vertical, grad_horizontal = np.gradient(box)
            x_deviation = np.std(grad_horizontal[1:-1, 1:-1])
            y_deviation = np.std(grad_vertical[1:-1, 1:-1])
            grad_score = np.abs(x_deviation - y_deviation)

            strength_total = 0
            sharpness_total = 0
            count = 0

            if box.shape[0] > box.shape[1]:
                for j in range(box.shape[1]):
                    arr = box[:, j]
                    gradient = np.abs(np.gradient(arr))
                    peak_value = np.max(gradient)
                    sorted_grad = np.sort(gradient)[::-1]
                    sharpness = peak_value - sorted_grad[1] if len(sorted_grad) > 1 else 0

                    strength_total += peak_value
                    sharpness_total += sharpness
                    count += 1

            elif box.shape[0] < box.shape[1]:
                for i in range(box.shape[0]):
                    arr = box[i, :]
                    gradient = np.abs(np.gradient(arr))
                    peak_value = np.max(gradient)
                    sorted_grad = np.sort(gradient)[::-1]
                    sharpness = peak_value - sorted_grad[1] if len(sorted_grad) > 1 else 0

                    strength_total += peak_value
                    sharpness_total += sharpness
                    count += 1

            else:
                return grad_score

            avg_strength = strength_total / count if count > 0 else 0
            avg_sharpness = sharpness_total / count if count > 0 else 0

            return (0.4 * grad_score) + (0.3 * avg_strength) + (0.3 * avg_sharpness)

        scores = {
            'top': orientation_score(top_box),
            'bottom': orientation_score(bottom_box),
            'left': orientation_score(left_box),
            'right': orientation_score(right_box)
        }

        vertical = scores['top'] + scores['bottom']
        horizontal = scores['left'] + scores['right']

        if vertical > horizontal:
            # Likely vertical fin orientation (up/down)
            self.is_vertical[folder_name] = False
        elif horizontal > vertical:
            # Likely horizontal fin orientation (left/right)
            self.is_vertical[folder_name] = True
        else:
            pass      

    def plate_edge_detection(self, folder_name):
        if folder_name not in self.heat_map_data or isinstance(self.heat_map_data[folder_name], str):
            return

        rows, cols = self.heat_map_data[folder_name].shape
        left_edge_locations = []
        right_edge_locations = []
        top_edge_locations = []
        bottom_edge_locations = []

        if self.is_vertical[folder_name] == True:
            for y in range(rows):
                row = self.heat_map_data[folder_name].iloc[y, :].values
                gradients = np.gradient(row)

                left_index = np.argmax(gradients)
                right_index = np.argmin(gradients)

                left_edge_locations.append(left_index)
                right_edge_locations.append(right_index)

            self.left_edges[folder_name] = statistics.mode(left_edge_locations)
            self.right_edges[folder_name] = statistics.mode(right_edge_locations)

            for x in range(self.left_edges[folder_name],self.right_edges[folder_name]):
                column = self.heat_map_data[folder_name].iloc[:,x].values
                smoothed_column = gaussian_filter1d(column, sigma=1)
                top_window = smoothed_column[:config.EDGE_SENSITIVITY]
                bottom_window = smoothed_column[-config.EDGE_SENSITIVITY:]

                top_gradients = np.gradient(top_window)
                top_index = np.argmax(top_gradients)

                bottom_gradients = np.gradient(bottom_window)
                bottom_index = len(column) - config.EDGE_SENSITIVITY + np.argmin(bottom_gradients)

                top_edge_locations.append(top_index)
                bottom_edge_locations.append(bottom_index)
                
            self.top_edges[folder_name] = statistics.mode(top_edge_locations)
            self.bottom_edges[folder_name] = statistics.mode(bottom_edge_locations)

            self.midline[folder_name] = (self.right_edges[folder_name] + self.left_edges[folder_name]) / 2
            
        elif self.is_vertical[folder_name] == False:
            for x in range(cols):
                column = self.heat_map_data[folder_name].iloc[:, x].values
                gradients = np.gradient(column)

                top_index = np.argmax(gradients)
                bottom_index = np.argmin(gradients)

                top_edge_locations.append(top_index)
                bottom_edge_locations.append(bottom_index)

            self.top_edges[folder_name] = statistics.mode(top_edge_locations)
            self.bottom_edges[folder_name] = statistics.mode(bottom_edge_locations)

            for y in range(self.top_edges[folder_name], self.bottom_edges[folder_name]):
                offset = 5
                row = self.heat_map_data[folder_name].iloc[y].values
                smoothed_row = gaussian_filter1d(row, sigma=1)

                left_window = smoothed_row[offset : offset + config.EDGE_SENSITIVITY]
                right_window = smoothed_row[-(offset + config.EDGE_SENSITIVITY) : -offset]

                left_gradients = np.gradient(left_window)
                right_gradients = np.gradient(right_window)

                left_index = offset + np.argmax(left_gradients)
                right_index = len(row) - offset - config.EDGE_SENSITIVITY + np.argmin(right_gradients)

                left_edge_locations.append(left_index)
                right_edge_locations.append(right_index)

            self.left_edges[folder_name] = statistics.mode(left_edge_locations)
            self.right_edges[folder_name] = statistics.mode(right_edge_locations)
            self.midline[folder_name] = (self.top_edges[folder_name] + self.bottom_edges[folder_name]) / 2


    def find_thermocouples(self, folder_name):
        if folder_name not in self.heat_map_data or isinstance(self.heat_map_data[folder_name], str):
            return
        
        if self.is_vertical[folder_name] == True:
            chamfered_x_pixels = math.trunc(((config.FIN_WIDTH-config.TC_C_HLOC)/config.FIN_WIDTH)*(self.right_edges[folder_name]-self.left_edges[folder_name]+1))+self.left_edges[folder_name]
            chamfered_y_pixels = math.trunc((config.TC_C_VLOC/config.FIN_HEIGHT)*(self.bottom_edges[folder_name]-self.top_edges[folder_name]+1))+self.top_edges[folder_name]
            self.c_tc_location[folder_name] = (chamfered_x_pixels, chamfered_y_pixels)

            filleted_x_pixels = math.trunc(((config.FIN_WIDTH-config.TC_F_HLOC)/config.FIN_WIDTH)*(self.right_edges[folder_name]-self.left_edges[folder_name]+1))+self.left_edges[folder_name]
            filleted_y_pixels = math.trunc(((config.FIN_HEIGHT-config.TC_F_VLOC)/config.FIN_HEIGHT)*(self.bottom_edges[folder_name]-self.top_edges[folder_name]+1))+self.top_edges[folder_name]
            self.f_tc_location[folder_name] = (filleted_x_pixels, filleted_y_pixels)

        elif self.is_vertical[folder_name] == False:
            chamfered_x_pixels = math.trunc(((config.FIN_HEIGHT-config.TC_C_VLOC)/config.FIN_HEIGHT)*(self.right_edges[folder_name]-self.left_edges[folder_name]+1))+self.left_edges[folder_name]
            chamfered_y_pixels = math.trunc(((config.FIN_WIDTH-config.TC_C_HLOC)/config.FIN_WIDTH)*(self.bottom_edges[folder_name]-self.top_edges[folder_name]+1))+self.top_edges[folder_name]
            self.c_tc_location[folder_name] = (chamfered_x_pixels, chamfered_y_pixels)

            filleted_x_pixels = math.trunc((config.TC_F_VLOC/config.FIN_HEIGHT)*(self.right_edges[folder_name]-self.left_edges[folder_name]+1))+self.left_edges[folder_name]
            filleted_y_pixels = math.trunc(((config.FIN_WIDTH-config.TC_F_HLOC)/config.FIN_WIDTH)*(self.bottom_edges[folder_name]-self.top_edges[folder_name]+1))+self.top_edges[folder_name]
            self.f_tc_location[folder_name] = (filleted_x_pixels, filleted_y_pixels)

    def get_averages(self, folder_name):
        if folder_name not in self.heat_map_data or isinstance(self.heat_map_data[folder_name], str):
                return

        if folder_name not in self.averages:
            self.averages[folder_name] = {
                'ChamferTemp_Arduino': None,
                'FilletTemp_Arduino': None,
                'FluidTemp_Arduino': None,
                'FlowRate_Arduino': None,
                'ChamferTemp_Flir': None,
                'FilletTemp_Flir': None
            }

        try:
            self.averages[folder_name]['ChamferTemp_Arduino'] = self.sensors_data[folder_name]['ChamferTemp_C'].mean()
            self.averages[folder_name]['FilletTemp_Arduino'] = self.sensors_data[folder_name]['FilletTemp_C'].mean()
            self.averages[folder_name]['FluidTemp_Arduino'] = self.sensors_data[folder_name]['FluidTemp_C'].mean()
            self.averages[folder_name]['FlowRate_Arduino'] = self.sensors_data[folder_name]['FlowRate_L_per_min'].mean()
        except Exception:
            pass

        try:
            self.averages[folder_name]['ChamferTemp_Flir'] = self.flir_chamfered_data[folder_name]['Chamfered_Side_TC'].mean()
            self.averages[folder_name]['FilletTemp_Flir'] = self.flir_filleted_data[folder_name]['Filleted_Side_TC'].mean()
        except Exception:
            pass

# ============================ UI Update Functions ==========================
    def on_tab_change(self):
        tab_name = self.experiments_tabs.get()
        heatmap_box_color = ''
        sensors_box_color = ''
        chamfered_box_color = ''
        filleted_box_color = ''
        ardunio_fillet_text = ''
        ardunio_chamfer_text = ''
        flir_fillet_text = ''
        flir_chamfer_text = ''
        arduino_fluid_temp_text = ''
        arduino_flow_rate_text = ''

        # Heatmap file
        if tab_name == 'Combined Plot':
            heatmap_status = 'N/A'
            heatmap_box_color = 'grey'
            chamfered_text = 'No Heatmap Selected'
            filleted_text = 'No Heatmap Selected'
            ardunio_fillet_text = 'N/A'
            ardunio_chamfer_text = 'N/A'
            flir_fillet_text = 'N/A'
            flir_chamfer_text = 'N/A'
            arduino_fluid_temp_text = 'N/A'
            arduino_flow_rate_text = 'N/A'
        elif tab_name in self.heat_map_data_filenames and self.heat_map_data_filenames[tab_name] != 'No File Found in Directory':
            heatmap_status = self.heat_map_data_filenames[tab_name]
            heatmap_box_color = 'green'
            chamfered_coords = self.c_tc_location[tab_name]
            filleted_coords = self.f_tc_location[tab_name]
            chamfered_text = f"({chamfered_coords[0]}, {chamfered_coords[1]})"
            filleted_text = f"({filleted_coords[0]}, {filleted_coords[1]})"
            try:
                ardunio_fillet_text = f"{self.averages[tab_name]['FilletTemp_Arduino']:.5f}"
                ardunio_chamfer_text = f"{self.averages[tab_name]['ChamferTemp_Arduino']:.5f}"
                arduino_fluid_temp_text = f"{self.averages[tab_name]['FluidTemp_Arduino']:.5f}"
                arduino_flow_rate_text = f"{self.averages[tab_name]['FlowRate_Arduino']:.5f}"
            except Exception:
                pass

            try:
                flir_fillet_text = f"{self.averages[tab_name]['FilletTemp_Flir']:.5f}"
                flir_chamfer_text = f"{self.averages[tab_name]['ChamferTemp_Flir']:.5f}"
            except Exception:
                pass

        else:
            heatmap_status = 'Heatmap Not Found'
            heatmap_box_color = 'red'
            chamfered_text = 'No Heatmap Selected'
            filleted_text = 'No Heatmap Selected'
            ardunio_fillet_text = 'N/A'
            ardunio_chamfer_text = 'N/A'
            flir_fillet_text = 'N/A'
            flir_chamfer_text = 'N/A'
            arduino_fluid_temp_text = 'N/A'
            arduino_flow_rate_text = 'N/A'

        # Sensors file
        if tab_name == 'Combined Plot':
            sensors_status = 'N/A'
            sensors_box_color = 'grey'
        elif tab_name in self.sensors_data_filenames and self.sensors_data_filenames[tab_name] != 'No File Found in Directory':
            sensors_status = self.sensors_data_filenames[tab_name]
            sensors_box_color = 'green'
        else:
            sensors_status = 'Sensor Data Not Found'
            sensors_box_color = 'red'

        # Chamfered FLIR data
        if tab_name == 'Combined Plot':
            chamfered_status = 'N/A'
            chamfered_box_color = 'grey'
        elif tab_name in self.flir_chamfered_data_filenames and self.flir_chamfered_data_filenames[tab_name] != 'No File Found in Directory':
            chamfered_status = self.flir_chamfered_data_filenames[tab_name]
            chamfered_box_color = 'green'
        else:
            chamfered_status = 'Chamfered FLIR Data Not Found'
            chamfered_box_color = 'red'

        # Filleted FLIR data
        if tab_name == 'Combined Plot':
            filleted_status = 'N/A'
            filleted_box_color = 'grey'
        elif tab_name in self.flir_filleted_data_filenames and self.flir_filleted_data_filenames[tab_name] != 'No File Found in Directory':
            filleted_status = self.flir_filleted_data_filenames[tab_name]
            filleted_box_color = 'green'
        else:
            filleted_status = 'Filleted FLIR Data Not Found'
            filleted_box_color = 'red'

        # Simulation data
        if tab_name == 'Combined Plot':
            simulation_file_status = 'N/A'
            simulation_file_box_color = 'grey'
        elif tab_name in self.simulation_data_filesnames and self.simulation_data_filesnames[tab_name] != 'No File Found in Directory':
            simulation_file_status = self.simulation_data_filesnames[tab_name]
            simulation_file_box_color = 'green'
        else:
            simulation_file_status = 'Simulation Results Not Found'
            simulation_file_box_color = 'red'

        # Update entries
        self.heatmap_file_label.configure(state='normal')
        self.heatmap_file_label.delete(0, 'end')
        self.heatmap_file_label.insert(0, heatmap_status)
        self.heatmap_file_label.configure(state='disabled', fg_color=heatmap_box_color)

        self.sensors_file_label.configure(state='normal')
        self.sensors_file_label.delete(0, 'end')
        self.sensors_file_label.insert(0, sensors_status)
        self.sensors_file_label.configure(state='disabled', fg_color=sensors_box_color)

        self.chamfered_file_label.configure(state='normal')
        self.chamfered_file_label.delete(0, 'end')
        self.chamfered_file_label.insert(0, chamfered_status)
        self.chamfered_file_label.configure(state='disabled', fg_color=chamfered_box_color)

        self.filleted_file_label.configure(state='normal')
        self.filleted_file_label.delete(0, 'end')
        self.filleted_file_label.insert(0, filleted_status)
        self.filleted_file_label.configure(state='disabled', fg_color=filleted_box_color)

        self.simulation_file_label.configure(state='normal')
        self.simulation_file_label.delete(0, 'end')
        self.simulation_file_label.insert(0, simulation_file_status)
        self.simulation_file_label.configure(state='disabled', fg_color=simulation_file_box_color)

        self.chamfered_tc_location.configure(state='normal')
        self.chamfered_tc_location.delete(0, 'end')
        self.chamfered_tc_location.insert(0, chamfered_text)
        self.chamfered_tc_location.configure(state='disabled')

        self.filleted_tc_location.configure(state='normal')
        self.filleted_tc_location.delete(0, 'end')
        self.filleted_tc_location.insert(0, filleted_text)
        self.filleted_tc_location.configure(state='disabled')

        self.chamfered_ave_box.configure(state='normal')
        self.chamfered_ave_box.delete(0, 'end')
        self.chamfered_ave_box.insert(0, ardunio_chamfer_text)
        self.chamfered_ave_box.configure(state='disabled')

        self.filleted_ave_box.configure(state='normal')
        self.filleted_ave_box.delete(0, 'end')
        self.filleted_ave_box.insert(0, ardunio_fillet_text)
        self.filleted_ave_box.configure(state='disabled')

        self.chamfered_flir_box.configure(state='normal')
        self.chamfered_flir_box.delete(0, 'end')
        self.chamfered_flir_box.insert(0, flir_chamfer_text)
        self.chamfered_flir_box.configure(state='disabled')

        self.filleted_flir_box.configure(state='normal')
        self.filleted_flir_box.delete(0, 'end')
        self.filleted_flir_box.insert(0, flir_fillet_text)
        self.filleted_flir_box.configure(state='disabled')

        self.fluid_temp_box.configure(state='normal')
        self.fluid_temp_box.delete(0, 'end')
        self.fluid_temp_box.insert(0, arduino_fluid_temp_text)
        self.fluid_temp_box.configure(state='disabled')

        self.flowrate_box.configure(state='normal')
        self.flowrate_box.delete(0, 'end')
        self.flowrate_box.insert(0, arduino_flow_rate_text)
        self.flowrate_box.configure(state='disabled')

        self.plot_heat_map()

# ============================ Plot Functions ==========================
    def plot_heat_map(self):
        tab_name = self.experiments_tabs.get()

        if tab_name not in self.heat_map_data or isinstance(self.heat_map_data[tab_name], str):
            return

        if tab_name in self.current_plot_canvas:
            self.current_plot_canvas[tab_name]['canvas'].get_tk_widget().destroy()
            self.current_plot_canvas[tab_name]['toolbar'].destroy()

        data = self.heat_map_data[tab_name]

        fig, ax = plt.subplots(figsize=config.FIGURE_SIZE)
        cax = ax.imshow(data, cmap='jet', origin='lower', aspect='auto')
        fig.colorbar(cax, ax=ax, label='Temperature (°C)')

        ax.set_title(f"Heat Map: {tab_name}")
        ax.set_xlabel('X (pixels)')
        ax.set_ylabel('Y (pixels)')
        ax.set_aspect('equal')
        ax.invert_yaxis()

        if self.is_vertical[tab_name] == True:
            chamfered_text_x = 0.99
            chamfered_text_y = 0.99
            filleted_text_x = 0.99
            filleted_text_y = 0.01
            chamfered_vertical = 'top'
            chamfered_horizontal = 'right'
            filleted_vertical = 'bottom'
            filleted_horizontal = 'right'

        elif self.is_vertical[tab_name] == False:
            chamfered_text_x = 0.99
            chamfered_text_y = 0.99
            filleted_text_x = 0.01
            filleted_text_y = 0.99
            chamfered_vertical = 'top'
            chamfered_horizontal = 'right'
            filleted_vertical = 'top'
            filleted_horizontal = 'left'        

        ax.text(chamfered_text_x, chamfered_text_y, 'Chamfered Side', transform=ax.transAxes,
            fontsize=10, color='white', verticalalignment=chamfered_vertical, horizontalalignment=chamfered_horizontal)

        ax.text(filleted_text_x, filleted_text_y, 'Filleted Side', transform=ax.transAxes,
            fontsize=10, color='white', verticalalignment=filleted_vertical, horizontalalignment=filleted_horizontal)

        if self.fin_box_checkbox.get() == 1:
            plot_color = 'black'
            line_thickness = 1
            line_style = '--'  # Dashed lines

            # Top edge
            ax.plot(
                [self.left_edges[tab_name], self.right_edges[tab_name]],
                [self.top_edges[tab_name], self.top_edges[tab_name]],
                color=plot_color, linewidth=line_thickness, linestyle=line_style
            )

            # Bottom edge
            ax.plot(
                [self.left_edges[tab_name], self.right_edges[tab_name]],
                [self.bottom_edges[tab_name], self.bottom_edges[tab_name]],
                color=plot_color, linewidth=line_thickness, linestyle=line_style
            )

            # Left edge
            ax.plot(
                [self.left_edges[tab_name], self.left_edges[tab_name]],
                [self.top_edges[tab_name], self.bottom_edges[tab_name]],
                color=plot_color, linewidth=line_thickness, linestyle=line_style
            )

            # Right edge
            ax.plot(
                [self.right_edges[tab_name], self.right_edges[tab_name]],
                [self.top_edges[tab_name], self.bottom_edges[tab_name]],
                color=plot_color, linewidth=line_thickness, linestyle=line_style
            )

        if self.midline_checkbox.get() == 1:
            plot_color = 'white'
            line_thickness = 1
            line_style = '--'  # Dashed line

            if self.is_vertical[tab_name] == True:
                ax.plot(
                    [self.midline[tab_name], self.midline[tab_name]],
                    [self.top_edges[tab_name]-5, self.bottom_edges[tab_name]+5],
                    color=plot_color, linewidth=line_thickness, linestyle=line_style
                )
            elif self.is_vertical[tab_name] == False:
                ax.plot(
                    [self.left_edges[tab_name]-5, self.right_edges[tab_name]+5],
                    [self.midline[tab_name], self.midline[tab_name]],
                    color=plot_color, linewidth=line_thickness, linestyle=line_style
                )

        if self.thermocouples_checkbox.get() == 1:
            box_size = 8
            half_box = box_size // 2
            
            # Chamfered TC
            if tab_name in self.c_tc_location:
                chamfered_x, chamfered_y = self.c_tc_location[tab_name]
                rect_c = plt.Rectangle(
                    (chamfered_x - half_box, chamfered_y - half_box),
                    box_size, box_size,
                    linewidth=2,
                    edgecolor='darkgreen',
                    facecolor='none'
                )
                ax.add_patch(rect_c)

            # Filleted TC
            if tab_name in self.f_tc_location:
                filleted_x, filleted_y = self.f_tc_location[tab_name]
                rect_f = plt.Rectangle(
                    (filleted_x - half_box, filleted_y - half_box),
                    box_size, box_size,
                    linewidth=2,
                    edgecolor='darkblue',
                    facecolor='none'
                )
                ax.add_patch(rect_f)

        master_frame = self.experiments_tabs.tab(tab_name)

        canvas = FigureCanvasTkAgg(fig, master=master_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

        toolbar = NavigationToolbar2Tk(canvas, master_frame)
        toolbar.update()
        toolbar.pack()

        self.current_plot_canvas[tab_name] = {'canvas': canvas, 'toolbar': toolbar}

    def plot_linear_profile(self):
        tab_name = self.experiments_tabs.get()
        if tab_name not in self.heat_map_data or isinstance(self.heat_map_data[tab_name], str):
            return

        if tab_name in self.current_plot_canvas:
            self.current_plot_canvas[tab_name]['canvas'].get_tk_widget().destroy()
            self.current_plot_canvas[tab_name]['toolbar'].destroy()

        data = self.heat_map_data[tab_name]

        if self.is_vertical[tab_name] == True:
            temperature_profile = data.iloc[self.top_edges[tab_name]:self.bottom_edges[tab_name], int(self.midline[tab_name])].values[::-1]
        if self.is_vertical[tab_name] == False:
            temperature_profile = data.iloc[int(self.midline[tab_name]), self.left_edges[tab_name]:self.right_edges[tab_name]].values

        num_points = len(temperature_profile)
        y_positions_mm = np.linspace(0, config.FIN_HEIGHT, num_points)

        fig, ax = plt.subplots(figsize=config.FIGURE_SIZE)
        ax.plot(y_positions_mm, temperature_profile, color='red', linewidth=2, label='Experimental Temperature Profile')

        if (self.simulation_checkbox.get() == 1
            and isinstance(self.simulation_data[tab_name], pd.DataFrame)
            and not self.simulation_data[tab_name].empty
        ):
            ax.plot(self.simulation_data[tab_name]['Location'], self.simulation_data[tab_name]['Temperature'], color='blue', linewidth=2, label='Simulated Temperature Profile')

        ax.set_title(f"Linear Temperature Profile at Midline: {tab_name}")
        ax.set_xlabel('Fin Height (mm)')
        ax.set_xlim(0, config.FIN_HEIGHT)
        y_min = temperature_profile.min() - 5
        y_max = temperature_profile.max() + 5
        ax.set_ylim(y_min, y_max)
        ax.set_ylabel('Temperature (°C)')
        ax.grid(True)

        ax.text(0.01, 0.99, 'Filleted Side', transform=ax.transAxes,
            fontsize=10, color='black', verticalalignment='top', horizontalalignment='left')

        ax.text(0.99, 0.99, 'Chamfered Side', transform=ax.transAxes,
            fontsize=10, color='black', verticalalignment='top', horizontalalignment='right')

        ax.legend(loc='lower right')

        master_frame = self.experiments_tabs.tab(tab_name)

        canvas = FigureCanvasTkAgg(fig, master=master_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

        toolbar = NavigationToolbar2Tk(canvas, master_frame)
        toolbar.update()
        toolbar.pack()

        self.current_plot_canvas[tab_name] = {'canvas': canvas, 'toolbar': toolbar}

    def plot_combined_linear_profile(self):
        combined_tab_name = 'Combined Plot'

        # Clean up old plots in the Combined tab
        if combined_tab_name in self.current_plot_canvas:
            self.current_plot_canvas[combined_tab_name]['canvas'].get_tk_widget().destroy()
            self.current_plot_canvas[combined_tab_name]['toolbar'].destroy()

        fig, ax = plt.subplots(figsize=config.FIGURE_SIZE)

        colors = ['red', 'blue', 'green', 'purple', 'orange', 'cyan', 'magenta', 'yellow', 'black', 'brown']
        color_index = 0

        for experiment in self.current_tabs:
            if experiment == 'Combined Plot':
                continue
            if experiment not in self.heat_map_data or isinstance(self.heat_map_data[experiment], str):
                continue

            data = self.heat_map_data[experiment]

            # Plot midline profile for each experiment
            if self.is_vertical[experiment] == True:
                temperature_profile = data.iloc[self.top_edges[experiment]:self.bottom_edges[experiment], int(self.midline[experiment])].values[::-1]
            if self.is_vertical[experiment] == False:
                temperature_profile = data.iloc[int(self.midline[experiment]), self.left_edges[experiment]:self.right_edges[experiment]].values
            num_points = len(temperature_profile)
            y_positions_mm = np.linspace(0, config.FIN_HEIGHT, num_points)

            ax.plot(y_positions_mm, temperature_profile, label=experiment, color=colors[color_index % len(colors)])
            color_index += 1

        ax.set_title('Combined Linear Temperature Profiles')
        ax.set_xlabel('Fin Height (mm)')
        ax.set_xlim(0, config.FIN_HEIGHT)
        ax.set_ylabel('Temperature (°C)')
        ax.grid(True)
        handles, labels = ax.get_legend_handles_labels()
        if labels:
                ax.legend(loc='upper right')

        ax.text(0.01, 0.01, 'Filleted Side', transform=ax.transAxes,
                fontsize=10, color='black', verticalalignment='bottom', horizontalalignment='left')
        ax.text(0.99, 0.01, 'Chamfered Side', transform=ax.transAxes,
                fontsize=10, color='black', verticalalignment='bottom', horizontalalignment='right')

        master_frame = self.experiments_tabs.tab(combined_tab_name)

        canvas = FigureCanvasTkAgg(fig, master=master_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

        toolbar = NavigationToolbar2Tk(canvas, master_frame)
        toolbar.update()
        toolbar.pack()

        self.current_plot_canvas[combined_tab_name] = {'canvas': canvas, 'toolbar': toolbar}


    def plot_temporal_data(self):
        tab_name = self.experiments_tabs.get()

        if tab_name not in self.heat_map_data or isinstance(self.heat_map_data[tab_name], str):
            return

        if tab_name in self.current_plot_canvas:
            self.current_plot_canvas[tab_name]['canvas'].get_tk_widget().destroy()
            self.current_plot_canvas[tab_name]['toolbar'].destroy()

        plot_tc = self.plot_thermocouple_temps.get() == 1
        plot_flir = self.plot_flir_temps.get() == 1
        plot_inlet = self.plot_inlet_temp.get() == 1
        plot_flow = self.plot_flow_rate.get() == 1

        # Exit if nothing is selected
        if not any([plot_tc, plot_flir, plot_inlet, plot_flow]):
            print("Nothing selected to plot.")
            return

        fig, ax1 = plt.subplots(figsize=config.FIGURE_SIZE)
        ax2 = None
        if (plot_tc or plot_flir or plot_inlet) and plot_flow:
            ax2 = ax1.twinx()

        time_series_list = []

        # ========== Plotting ==========
        try:
            if plot_tc:
                ax1.plot(self.sensors_data[tab_name]['Absolute_Time'], self.sensors_data[tab_name]['ChamferTemp_C'], color='green', linestyle='-', label='TC Reading, Chamfered Edge (Inst)')
                ax1.plot(self.sensors_data[tab_name]['Absolute_Time'], self.sensors_data[tab_name]['FilletTemp_C'], color='red', linestyle='-', label='TC Reading, Filleted Edge (Inst)')

                ax1.axhline(y=self.averages[tab_name]['ChamferTemp_Arduino'], color='green', linestyle='--', label='TC Reading, Chamfered Edge (Avg)')
                ax1.axhline(y=self.averages[tab_name]['FilletTemp_Arduino'], color='red', linestyle='--', label='TC Reading, Filleted Edge (Avg)')

                time_series_list.append(self.sensors_data[tab_name]['Absolute_Time'])
        except Exception:
            pass

        try:
            if plot_flir:
                ax1.plot(self.flir_chamfered_data[tab_name]['time'], self.flir_chamfered_data[tab_name]['Chamfered_Side_TC'], color='cyan', linestyle='-', label='FLIR Reading, Chamfered Edge (Inst)')
                ax1.plot(self.flir_filleted_data[tab_name]['time'], self.flir_filleted_data[tab_name]['Filleted_Side_TC'], color='orange', linestyle='-', label='FLIR Reading, Filleted Edge (Inst)')

                ax1.axhline(y=self.averages[tab_name]['ChamferTemp_Flir'], color='cyan', linestyle='--', label='FLIR Reading, Chamfered Edge (Avg)')
                ax1.axhline(y=self.averages[tab_name]['FilletTemp_Flir'], color='orange', linestyle='--', label='FLIR Reading, Filleted Edge (Avg)')

                time_series_list.append(self.flir_chamfered_data[tab_name]['time'])
                time_series_list.append(self.flir_filleted_data[tab_name]['time'])
        except Exception:
            pass

        try:
            if plot_inlet:
                ax1.plot(self.sensors_data[tab_name]['Absolute_Time'], self.sensors_data[tab_name]['FluidTemp_C'], color='purple', linestyle='-', label='Fluid Inlet Temp (Inst)')

                ax1.axhline(y=self.averages[tab_name]['FluidTemp_Arduino'], color='purple', linestyle='--', label='Fluid Inlet Temp (Avg)')

                time_series_list.append(self.sensors_data[tab_name]['Absolute_Time'])
        except Exception:
            pass

        try:
            if plot_flow:
                target_ax = ax2 if (plot_tc or plot_flir or plot_inlet) else ax1  # Use ax1 if no temperatures are selected

                target_ax.plot(self.sensors_data[tab_name]['Absolute_Time'], self.sensors_data[tab_name]['FlowRate_L_per_min'], color='blue', linestyle='-', label='Flow Rate (Inst)')

                target_ax.axhline(y=self.averages[tab_name]['FlowRate_Arduino'], color='blue', linestyle='--', label='Flow Rate (Avg)')

                time_series_list.append(self.sensors_data[tab_name]['Absolute_Time'])
        except Exception:
            pass

        # ========== Axis Formatting ==========
        if time_series_list:
            min_time = min(series.min() for series in time_series_list)
            max_time = max(series.max() for series in time_series_list)
            ax1.set_xlim(min_time, max_time)

        ax1.set_xlabel('Time (Minutes)')
        ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax1.grid(True)
        for label in ax1.get_xticklabels():
            label.set_rotation(45)

        if plot_tc or plot_flir or plot_inlet:
            ax1.set_ylabel('Temperature (°C)')

        if ax2:
            ax2.set_ylabel('Flow Rate (LPM)', color='blue')
            ax2.tick_params(axis='y', colors='blue')
            ax2.spines['right'].set_color('blue')

        ax1.set_title(f"Temperature and Flow Rate vs Time for Experiment: {tab_name}")

        # ========== Legend and Explanatory Box ==========
        custom_lines = [
            Line2D([0], [0], color='green', lw=2, label='Chamfered Edge (TC)'),
            Line2D([0], [0], color='red', lw=2, label='Filleted Edge (TC)'),
            Line2D([0], [0], color='cyan', lw=2, label='Chamfered Edge (FLIR)'),
            Line2D([0], [0], color='orange', lw=2, label='Filleted Edge (FLIR)'),
            Line2D([0], [0], color='purple', lw=2, label='Fluid Inlet Temp'),
            Line2D([0], [0], color='blue', lw=2, label='Flow Rate'),
        ]

        ax1.legend(handles=custom_lines, loc='lower right')

        ax1.text(0.638, 0.08,
                'Line Styles:\n-  Instantaneous\n-- Averaged',
                transform=ax1.transAxes,
                fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        plt.tight_layout()

        # ========== Embedding in GUI ==========
        master_frame = self.experiments_tabs.tab(tab_name)
        canvas = FigureCanvasTkAgg(fig, master=master_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

        toolbar = NavigationToolbar2Tk(canvas, master_frame)
        toolbar.update()
        toolbar.pack()

        self.current_plot_canvas[tab_name] = {'canvas': canvas, 'toolbar': toolbar}
