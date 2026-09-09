### Aquisition data - Phase resolved method ###
### Daniel Santos ###


# %%
import time
import yaml

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from drawnow import drawnow
from gpg_devices_v03 import Standford_SR830, Thorlabs_ITC4002QCL, Rigol_DG832
# %%


plt.ion()

def ramp_lasers(laserNH3, laserN2O):
    """
    Turn on the lasers gradually:
    1. TEC on manually (temperature control)
    2. Set temperature: temp_i = 25 to tempNH3_f = 46.450 and tempN2O_f = 41.560 in celcius (step 0.1)
    3. LD on
    4. Set current
    """

    temp_NH3_target = 46.450  # °C
    temp_N2O_target = 41.560  # °C
    temp_i = 25.000           # °C
    step_temp = 0.1           # °C
    delay_temp = 0.5          # time between the temperature step

    current_NH3_target = 520.0e-3 # 520.0 mA
    current_N2O_target = 293.6e-3 # 293.6 mA
    step_current = 5e-3           # 5 mA
    delay_current = 0.5           # time between the current step

    print("\n Turn on the LD")
    laserNH3.ld_on()
    laserN2O.ld_on()
    print("LD on")

    for i in range(5, 0, -1):
        print(f" \n    Wating {i} seconds setting current", end="\r")
        time.sleep(1)

    print("\n Setting current")

    current = 0
    while current < current_NH3_target:
        current += step_current
        if current > current_NH3_target:
            current = current_NH3_target
        laserNH3.set_laser_current(current)
        time.sleep(delay_current)

    current = 0
    while current < current_N2O_target:
        current += step_current
        if current > current_N2O_target:
            current = current_N2O_target
        laserN2O.set_laser_current(current)
        time.sleep(delay_current)

    print("\n Setting temperature")

    time.sleep(1)

    temp_current = temp_i
    while temp_current < temp_NH3_target:
        temp_current += step_temp
        if temp_current > temp_NH3_target:
            temp_current = temp_NH3_target
        laserNH3.set_temp(temp_current)
        time.sleep(delay_temp)

    temp_current = temp_i
    while temp_current < temp_N2O_target:
        temp_current += step_temp
        if temp_current > temp_N2O_target:
            temp_current = temp_N2O_target
        laserN2O.set_temp(temp_current)
        time.sleep(delay_temp)

    print("\n Temperature stabilization...")
    for i in range(10, 0, -1):
        print(f"\n    Wating {i} seconds...", end="\r")
        time.sleep(1)
    print("\n Temperatures have stabilized.")


def long_term_measurement(lockin, laserNH3, laserN2O, generator) -> dict:
    
    """
Perform a long term measurement recording data from
the lock-in amplifier and two laser sources.

Parameters:
    lockin: An instance of Standford_SR830 for reading lock-in amplifier data.
    laserNH3: An instance of Thorlabs_ITC4002QCL for NH3 laser (controlled by generator channel 1).
    laserN2O: An instance of Thorlabs_ITC4002QCL for N2O laser (controlled by generator channel 2).
    generator: An instance of Rigol_DG832 for function generator (dual channel).

Returns:
    dict: A dictionary containing recorded data with keys:
        'X', 'Y', 'R', 'R_phase', 'FG_phase', 'f', 't_NH3', 't_N2O', and 'time'.
"""

    plt.cla()
    records = {"X": [], "Y": [], "R": [], "R_phase": [], "FG_phase": [], "f": [],
               "t_NH3": [], "t_N2O": [], "time": []}

    t = time.time()
    records["time"].append(t)

    while True:
        time.sleep(1)
        lockin.read()
        laserNH3.read_temp()
        laserN2O.read_temp()

        records["X"].append(lockin.X)
        records["Y"].append(lockin.Y)
        records["R"].append(lockin.R)
        records["R_phase"].append(lockin.R_phase)
        records["FG_phase"].append(generator.FG_phase)
        records["f"].append(lockin.f)
        records["t_NH3"].append(laserNH3.t_NH3)
        records["t_N2O"].append(laserN2O.t_N2O)
        records["time"].append(time.time() - t)

        drawnow(lambda: plot_XY(X=records["X"], Y=records["Y"]))
        plt.pause(0.001)


return records

def plot_XY(X, Y, time):
    plt.cla()
    
    plt.subplot(2, 1, 1)
    plt.xlabel("Time (s)")
    plt.ylabel("N2O Signal (V)")
    plt.plot(time, X, "r-")

    plt.subplot(2, 1, 2)
    plt.xlabel("Time (s)")
    plt.ylabel("NH3 Signal (V)")
    plt.plot(time, Y, "b-")

    plt.tight_layout()
        

