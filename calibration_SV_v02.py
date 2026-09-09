# %%

from cmath import phase
import os
import time

import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tkinter import Button, END, Entry, Label, Tk, filedialog

from drawnow import drawnow

from gpg_devices_v01 import Standford_SR830, Thorlabs_ITC4002QCL, Rigol_DG832


# %%


def stop():
    """Stop scanning by setting the running flag to False."""
    global running
    running = False


def calibration(lockin, laser) -> dict:
    """
    Perform calibration by reading data from the lock-in amplifier and laser temperature source.

    Parameters:
        lockin (Lockin): An instance of the Lockin class for reading lock-in amplifier data.
        laser (Laser): An instance of the Laser class for reading laser temperature data.

    Returns:
        dict: A dictionary containing recorded data with keys 'X', 'Y', 'R', 'phase', 'f', and 't'.

    Keys in the returned dictionary:
        X: in-phase component
        Y: quadrature component
        R: magnitude
        phase: phase
        f: frequency
        t: temperature
    """
    records = {"X": [], "Y": [], "R": [], "phase": [], "f": [], "t": []}

    plt.cla()
    global running
    running = True

    path = filedialog.asksaveasfile(mode="w", defaultextension=".dat")
    print(running)

    # records = Records()
    while running:
        lockin.read()
        laser.read_temp()

        records["X"].append(lockin.X)
        records["Y"].append(lockin.Y)
        records["R"].append(lockin.R)
        records["phase"].append(lockin.phase)
        records["f"].append(lockin.f)
        records["t"].append(laser.t)

        drawnow(plot_calibration(records["R"]))
        time.sleep(1)
        with open(path.name, "a") as file:
            file.writelines(
                "%e, %e, %e, %f, %.3f\n"
                % (lockin.X, lockin.Y, lockin.R, lockin.f, laser.t)
            )

    return records


def ramp_frequency(
    lockin, laser, source, f_start, f_end, f_step, amplitude=80e-3, path=None
) -> dict:
    """
    Perform a frequency ramp by adjusting the frequency of the source and recording data from the lock-in amplifier and laser temperature source.

    Parameters:
        lockin (Lockin): An instance of the Lockin class for reading lock-in amplifier data.
        laser (Laser): An instance of the Laser class for reading laser temperature data.
        source (DG832): An instance of the DG832 class for adjusting frequency.
        f_start (float): The starting frequency for the ramp.
        f_end (float): The ending frequency for the ramp.
        f_step (float): The frequency step size for the ramp.
        path (str): The file path for saving the recorded data.
    Returns:
        dict: A dictionary containing recorded data with keys 'X', 'Y', 'R', 'phase', 'f', and 't'.
    """
    plt.cla()
    records = {"X": [], "Y": [], "R": [], "phase": [], "f": [], "t": []}

    # source.set_waveform('SINusoid')
    # source.set_offset(509.6e-3)
    source.set_amplitude(amplitude)
    source.set_frequency(f_start)

    for f in np.arange(f_start, f_end + f_step, f_step):
        source.set_frequency(f)
        time.sleep(1)

        lockin.read()
        laser.read_temp()

        records["X"].append(lockin.X)
        records["Y"].append(lockin.Y)
        records["R"].append(lockin.R)
        records["phase"].append(lockin.phase)
        # records['f'].append(lockin.f)
        records["f"].append(f)
        records["t"].append(laser.t)

        drawnow(lambda: plot_calibration(f=records["f"], R=records["R"]))
        # if path:
        #     with open(path.name, 'a') as file:
        #         file.writelines('%e, %e, %e, %f, %.3f\n' % (lockin.X, lockin.Y, lockin.R, lockin.f, laser.t))

    print(f"R = {records['R']}")
    plot_calibration(records["R"])
    return records


def plot_calibration(f, R):

    # plt.clf()
    plt.title("Photoacoustic Signal")
    plt.grid(True)
    plt.xlabel("Frequency / Hz")
    plt.ylabel("Magnitude / V")
    plt.plot(f, R, "r-")
    # plt.show()


def gui_calibration(root, lockin, laser, source=None):

    # calibration
    # global tempCalib,tempin,tempfim, temp, tdelta, prec, num, frec, freqin, freqfim, freqprec

    Label(root, width=20, font=("Helvica", 16), text="Measure").place(x=100, y=10)

    f_entry = Entry(root, width=15)
    f_entry.insert(END, "3860")
    f_entry.place(x=150, y=50)
    Label(root, width=10, text="freq").place(x=58, y=50)
    if source is not None:
        source.set_frequency(f_entry.get())

    t_entry = Entry(root, width=15)
    t_entry.place(x=150, y=80)
    Label(root, width=10, text="Temp").place(x=58, y=80)

    Button(
        root, width=12, text="Start", command=lambda: calibration(lockin, laser)
    ).place(x=300, y=150)


if __name__ == "__main__":
    # lockin = None
    # laser = None

    lockin = Standford_SR830()
    laser = Thorlabs_ITC4002QCL()  # NH3
    source = Rigol_DG832()

    f_start = 3900
    f_end = 4000
    f_step = 5.0
    amplitude = 80e-3

    path = f"{os.getcwd()}/data/frequency_ramp_data_01.dat"

    ramp_frequency(
        lockin,
        laser,
        source,
        f_start=f_start,
        f_end=f_end,
        f_step=f_step,
        amplitude=amplitude,
        path=path,
    )

    # running = False
    # output_file = None

    # root = Tk()
    # root.geometry("500x550")
    # root.title("Photoacoustic Spectroscopy for one Controller")

    # gui_calibration(root, lockin, laser, source)
    # root.mainloop()
