# %%

import os
import time

import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyvisa as visa

from tkinter import Button, END, Entry, Label, Tk, filedialog

from drawnow import drawnow

# %%


class Lockin:
    def __init__(self, resource_name="GPIB0::8::INSTR") -> None:
        self.X = None  # in-phase component
        self.Y = None  # quadrature component
        self.R = None  # magnitude
        self.phase = None  # phase
        self.f = None  # frequency

        self._visa = visa.ResourceManager().open_resource(resource_name)
        self._visa.timeout = 5000  # Increase the timeout to 5 seconds
        self._visa.write_termination = "\n"
        self._visa.read_termination = "\n"
        self._visa.clear()  # Clear the buffer of SR830

    def read(self):
        self.X, self.Y, self.R, self.phase, self.f = map(
            np.float64, self._visa.query("SNAP?1,2,3,4,9").split(",")
        )

    def write_frequency(self, frequency):
        self._visa.write(f"FREQ {frequency}")


class Laser:
    """
    Class to control the laser temperature source.

    Parameters:
        resource_name (str): The VISA resource name for the laser temperature source.
            Default:     'USB0::0x1313::0x804A::M00884527::INSTR' for NH3 laser.
            Alternative: 'USB0::0x1313::0x804A::M00977996::INSTR' for N2O laser.

    Attributes:
        temp (float): The current temperature of the laser.
        _visa (pyvisa.resources.Resource): The VISA resource for communication with the laser.

    Methods:
        set_temp(temperature): Sets the temperature of the laser to the specified value.
        read_temp(): Reads the current temperature of the laser and updates the temp attribute.

    """

    def __init__(self, resource_name="USB0::0x1313::0x804A::M00884527::INSTR") -> None:
        self.t = None  # temperature

        self._visa = visa.ResourceManager().open_resource(resource_name)

    def set_temp(self, temperature):
        self._visa.write(f"SOUR2:TEMP {temperature}")

    def read_temp(self) -> float:
        self.t = float(self._visa.query("MEAS:TEMP?"))
        return self.t


class Records:
    def __init__(self):
        self.X = []  # in-phase component
        self.Y = []  # quadrature component
        self.R = []  # magnitude
        self.phase = []  # phase
        self.f = []  # frequency
        self.t = []  # temperature


def stop():
    """Stop scanning by setting the running flag to False."""
    global running
    running = False
    file.close()


def calibration(lockin, laser):
    plt.cla()
    global running
    running = True
    global file
    file = filedialog.asksaveasfile(mode="w", defaultextension=".dat")
    print(running)

    records = Records()
    while running:
        lockin.read()
        laser.read_temp()

        records.X.append(lockin.X)
        records.Y.append(lockin.Y)
        records.R.append(lockin.R)
        records.phase.append(lockin.phase)
        records.f.append(lockin.f)
        records.t.append(laser.t)

        drawnow(plot_calibration(records.R))
        time.sleep(1)
        file.writelines(
            "%e, %e, %e, %f, %.3f\n" % (lockin.X, lockin.Y, lockin.R, lockin.f, laser.t)
        )


def plot_calibration(R):

    plt.clf()
    plt.title("Photoacoustic Signal")
    plt.grid(True)
    plt.xlabel("Samples / AU")
    plt.ylabel("Magnitude / V")
    plt.plot(R, "r-")


def input_parameters(root):

    # calibration
    global \
        tempCalib, \
        tempin, \
        tempfim, \
        temp, \
        tdelta, \
        prec, \
        num, \
        frec, \
        freqin, \
        freqfim, \
        freqprec

    Label(root, width=20, font=("Helvica", 16), text="Measure").place(x=100, y=10)

    freq = Entry(root, width=5)
    freq.insert(END, "3860")
    freq.place(x=150, y=50)
    Label(root, width=10, text="freq").place(x=58, y=50)

    tempCalib = Entry(root, width=5)
    tempCalib.place(x=150, y=80)
    Label(root, width=10, text="Temp").place(x=58, y=80)

    Button(
        root, width=12, text="Start", command=lambda: calibration(lockin, laser)
    ).place(x=230, y=65)


if __name__ == "__main__":
    lockin = Lockin()
    laser = Laser()  # NH3

    running = False
    output_file = None

    root = Tk()
    root.geometry("500x550")
    root.title("Photoacoustic Spectroscopy for one Controller")

    input_parameters(root)
    root.mainloop()
