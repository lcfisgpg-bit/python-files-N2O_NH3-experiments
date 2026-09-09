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


def _entry_float(widget, label, default=None):
    raw_value = widget.get().strip()
    if not raw_value:
        if default is not None:
            return default
        raise ValueError(f"{label} is required")
    return float(raw_value)


def _open_output_file():
    path = filedialog.asksaveasfilename(defaultextension=".dat")
    if not path:
        return None
    return open(path, mode="w", encoding="utf-8")


def _records_frame(records):
    return pd.DataFrame.from_records(records)


# %%


def makefig_temp(df):
    if df.empty:
        return

    plt.clf()
    _, axes = plt.subplots(3, 1, sharex=True)
    axes[0].set_title("Photoacoustic Signal")
    axes[0].grid(True)
    axes[0].set_ylabel("Signal R (V)")
    axes[0].plot(df["temp_set"], df["R"], "r-", label="Absolute")
    axes[0].legend(loc="upper right")

    axes[1].set_ylabel("Signal X (V)")
    axes[1].plot(df["temp_set"], np.abs(df["X"]), "r-", label="x-axis")
    axes[1].legend(loc="upper right")

    axes[2].set_xlabel("Temperature (C)")
    axes[2].set_ylabel("Signal Y (V)")
    axes[2].plot(df["temp_set"], np.abs(df["Y"]), "r-", label="y-axis")
    axes[2].legend(loc="upper right")

    plt.tight_layout()


def makefig_freq(df):
    if df.empty:
        return

    plt.clf()
    plt.title("Photoacoustic Signal")
    plt.grid(True)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude (V)")
    plt.plot(df["f"], df["R_calculated"], "r-", label="Módulo")
    plt.legend(loc="upper right")


def Calibrate():
    records = []

    plt.cla()
    global running
    global output_file
    running = True
    output_file = _open_output_file()
    if output_file is None:
        running = False
        return None

    try:
        calibration_frequency = _entry_float(
            calibration_freq_entry, "calibration frequency"
        )
        lockin.write(f"FREQ {calibration_frequency}")

        calibration_temperature = _entry_float(
            tempCalib, "calibration temperature", default=None
        )
        if calibration_temperature is not None:
            laser.write(f"SOUR2:TEMP {calibration_temperature}")

        while running:
            dadosx, dadosy, dadosr, dadosphase = map(
                np.float64, lockin.query("SNAP?1,2,3,4").split(",")
            )
            dadost = float(laser.query("MEAS:TEMP?"))
            dadosf = float(lockin.query("SNAP?9"))

            records.append(
                {
                    "X": dadosx,
                    "Y": dadosy,
                    "R": dadosr,
                    "phase": dadosphase,
                    "f": dadosf,
                    "temp_measured": dadost,
                }
            )

            drawnow(lambda: makefig_calib(_records_frame(records)))
            time.sleep(1)
            output_file.write(
                "%e, %e, %e, %f, %.3f\n" % (dadosx, dadosy, dadosr, dadosphase, dadost)
            )

        return _records_frame(records)
    finally:
        output_file.close()
        output_file = None


def RampaTemperatura():
    records = []

    plt.cla()
    global output_file

    ti = _entry_float(tempin, "temperature start")
    tf = _entry_float(tempfim, "temperature end")
    tdel = _entry_float(tdelta, "temperature step")
    frequency_value = _entry_float(temp_scan_freq, "scan frequency", default=None)

    output_file = _open_output_file()
    if output_file is None:
        return None

    try:
        if frequency_value is not None:
            lockin.write(f"FREQ {frequency_value}")

        laser.write(f"SOUR2:TEMP {ti}")
        time.sleep(3)

        for temperature_setpoint in np.arange(ti, tf + tdel, tdel):
            laser.write(f"SOUR2:TEMP {temperature_setpoint}")
            time.sleep(2)

            dadosx, dadosy, dadosr, dadosphase = map(
                np.float64, lockin.query("SNAP?1,2,3,4").split(",")
            )
            dadost = float(laser.query("MEAS:TEMP?"))

            records.append(
                {
                    "X": dadosx,
                    "Y": dadosy,
                    "R": dadosr,
                    "phase": dadosphase,
                    "f": frequency_value if frequency_value is not None else np.nan,
                    "temp_set": float(temperature_setpoint),
                    "temp_measured": dadost,
                }
            )

            drawnow(lambda: makefig_temp(_records_frame(records)))
            output_file.write(
                "%e, %e, %e, %f, %.3f\n" % (dadosx, dadosy, dadosr, dadosphase, dadost)
            )

        print("medida concluída")
        return _records_frame(records)
    finally:
        output_file.close()
        output_file = None


def RampaFrequencia():
    records = []

    plt.cla()

    global output_file
    temperature_value = _entry_float(freq_temp, "temperature")
    fi = _entry_float(freqin, "frequency start")
    ff = _entry_float(freqfim, "frequency end")
    pc = _entry_float(freqprec, "frequency step")

    output_file = _open_output_file()
    if output_file is None:
        return None

    try:
        laser.write(f"SOUR2:TEMP {temperature_value}")
        time.sleep(9)
        lockin.write("FMOD1")

        for frequency_value in np.arange(fi, ff + pc, pc):
            lockin.write(f"FREQ {frequency_value}")
            time.sleep(1)

            dadosx, dadosy, dadosr, dadosphase = map(
                np.float64, lockin.query("SNAP?1,2,3,4").split(",")
            )
            dadost = float(laser.query("MEAS:TEMP?"))
            dadosf = float(lockin.query("SNAP?9"))
            dados_calculated = float(np.sqrt(dadosx**2 + dadosy**2))

            records.append(
                {
                    "X": dadosx,
                    "Y": dadosy,
                    "R": dadosr,
                    "phase": dadosphase,
                    "f": dadosf,
                    "temp_measured": dadost,
                    "R_calculated": dados_calculated,
                }
            )

            drawnow(lambda: makefig_freq(_records_frame(records)))
            output_file.write(
                "%e, %e, %e, %f, %.3f, %.3f\n"
                % (dadosx, dadosy, dadosr, dadosphase, dadost, dadosf)
            )

        print("medida concluída")
        return _records_frame(records)
    finally:
        output_file.close()
        output_file = None


def stop():
    """Stop scanning by setting the running flag to False."""
    global running
    global output_file
    running = False
    if output_file is not None:
        output_file.close()
        output_file = None


def parametros_entrada(root):

    # Calibração

    global \
        calibration_freq_entry, \
        tempCalib, \
        temp_scan_freq, \
        tempin, \
        tempfim, \
        freq_temp_entry, \
        tdelta, \
        freqin, \
        freqfim, \
        freqprec

    Label(root, width=20, font=("Helvica", 16), text="Measure").place(x=100, y=10)

    calibration_freq_entry = Entry(root, width=5)
    calibration_freq_entry.insert(END, "3860")
    calibration_freq_entry.place(x=150, y=50)
    Label(root, width=10, text="freq").place(x=58, y=50)

    tempCalib = Entry(root, width=5)
    tempCalib.place(x=150, y=80)
    Label(root, width=10, text="Temp").place(x=58, y=80)

    Button(root, width=12, text="Start", command=Calibrate).place(x=230, y=65)

    Label(root, width=20, font=("Helvica", 16), text="Scan of temperature").place(
        x=100, y=120
    )

    # Rampa de temperatura

    temp_scan_freq = Entry(root, width=5)
    temp_scan_freq.insert(END, "3860")
    temp_scan_freq.place(x=150, y=170)
    Label(root, width=10, text="freq").place(x=58, y=170)

    tempin = Entry(root, width=5)
    tempin.place(x=150, y=200)
    Label(root, width=10, text="T Start").place(x=58, y=200)

    tempfim = Entry(root, width=5)
    tempfim.place(x=150, y=230)
    Label(root, width=10, text="T final").place(x=58, y=230)

    tdelta = Entry(root, width=5)
    tdelta.place(x=150, y=260)
    Label(root, width=10, text="Step").place(x=58, y=260)

    Button(root, width=12, text="Start Scan", command=RampaTemperatura).place(
        x=230, y=210
    )

    Label(root, width=20, font=("Helvica", 16), text="Scan of frequency").place(
        x=100, y=300
    )

    # Rampa de frequência

    freq_temp_entry = Entry(root, width=5)
    freq_temp_entry.place(x=150, y=340)
    Label(root, width=10, text="Temp").place(x=58, y=340)

    freqin = Entry(root, width=5)
    freqin.place(x=150, y=370)
    Label(root, width=10, text="freq Start").place(x=58, y=370)

    freqfim = Entry(root, width=5)
    freqfim.place(x=150, y=400)
    Label(root, width=10, text="freq final").place(x=58, y=400)

    freqprec = Entry(root, width=5)
    freqprec.place(x=150, y=430)
    Label(root, width=10, text="Step").place(x=58, y=430)

    Button(root, width=12, text="Start Scan", command=RampaFrequencia).place(
        x=230, y=380
    )

    Button(root, width=20, text="Stop any function", command=stop).place(x=130, y=470)


root = Tk()
root.geometry("500x550")
root.title("Photoacoustic Spectroscopy for one Controller")

parametros_entrada(root)
root.mainloop()
