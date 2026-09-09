# %%

from cmath import phase
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


class DG832:
    def __init__(
        self,
        resource_name="USB0::0x1AB1::0x643::DG8A244803802::INSTR",
        waveform="SINusoid",
        amplitude=1.0,
        offset=0.0,
        frequency=1000.0,
    ) -> None:
        self.waveform = waveform
        self.amplitude = amplitude
        self.offset = offset
        self.frequency = frequency

        self._visa = visa.ResourceManager().open_resource(resource_name)
        self._visa.timeout = 5000  # Increase the timeout to 5 seconds
        self._visa.write_termination = "\n"
        self._visa.read_termination = "\n"
        self._visa.clear()  # Clear the buffer of DG832

    def set_offset(self, channel=1, voltage=0.0):
        self.offset = voltage
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        self._visa.write(f":SOURce{channel}:VOLTage:OFFSet {self.offset}")

    def set_amplitude(self, channel=1, voltage=0.0):
        self.amplitude = voltage
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        self._visa.write(f":SOURce{channel}:VOLTage:AMPLitude {self.amplitude}")

    def set_waveform(self, waveform, channel=1):
        if waveform not in [
            "SINusoid",
            "SQUare",
            "TRIangle",
            "RAMP",
            "NRAMp",
            "NOISe",
            "ARB",
        ]:
            raise ValueError(
                "Waveform must be one of 'SINusoid', 'SQUare', 'TRIangle', 'RAMP', 'NRAMp', 'NOISe', or 'ARB'."
            )
        self.waveform = waveform
        self._visa.write(f":SOURce{channel}:AM:INTernal:FUNCtion {waveform}")

    def set_frequency(self, frequency, channel=1):
        self.frequency = frequency
        self._visa.write(f":SOURce{channel}:FREQuency {frequency}")

    def set_phase(self, phase, channel=1):
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        self._visa.write(f":SOURce{channel}:PHASe:COUPle:OFFSet {phase}")


# class Records:
#     def __init__(self):
#         self.X = [] # in-phase component
#         self.Y = [] # quadrature component
#         self.R = [] # magnitude
#         self.phase = [] # phase
#         self.f = [] # frequency
#         self.t = [] # temperature


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
        records["f"].append(lockin.f)
        records["t"].append(laser.t)

        drawnow(plot_calibration(records["R"]))
        if path:
            with open(path.name, "a") as file:
                file.writelines(
                    "%e, %e, %e, %f, %.3f\n"
                    % (lockin.X, lockin.Y, lockin.R, lockin.f, laser.t)
                )

    return records


def plot_calibration(R):

    plt.clf()
    plt.title("Photoacoustic Signal")
    plt.grid(True)
    plt.xlabel("Samples / AU")
    plt.ylabel("Magnitude / V")
    plt.plot(R, "r-")


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
    lockin = Lockin()
    laser = Laser()  # NH3
    # lockin = None
    # laser = None
    source = DG832()
    path = f"{os.getcwd()}/data/frequency_ramp_data_01.dat"

    ramp_frequency(
        lockin,
        laser,
        source,
        f_start=3600,
        f_end=4000,
        f_step=5.0,
        amplitude=80e-3,
        path=path,
    )

    # running = False
    # output_file = None

    # root = Tk()
    # root.geometry("500x550")
    # root.title("Photoacoustic Spectroscopy for one Controller")

    # gui_calibration(root, lockin, laser, source)
    # root.mainloop()
