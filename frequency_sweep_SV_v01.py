# %%
import os
import time
# import matplotlib

# matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from drawnow import drawnow
from gpg_devices_v01 import Standford_SR830, Thorlabs_ITC4002QCL, Rigol_DG832


# %%
def frequency_sweep(
    lockin, laser, source, f_start, f_end, f_step, amplitude=80e-3, path=None
) -> dict:
    """
    Perform a frequency sweep by adjusting the frequency of the source and recording data from the lock-in amplifier and laser temperature source.

    Parameters:
        lockin (Lockin): An instance of the Lockin class for reading lock-in amplifier data.
        laser (Laser): An instance of the Laser class for reading laser temperature data.
        source (DG832): An instance of the DG832 class for adjusting frequency.
        f_start (float): The starting frequency for the sweep.
        f_end (float): The ending frequency for the sweep.
        f_step (float): The frequency step size for the sweep.
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

        drawnow(lambda: plot_fR(f=records["f"], R=records["R"]))

    if path:
        df = pd.DataFrame(records)
        df.set_index("f", inplace=True)
        df.to_csv(path, header=True, sep=",", float_format="%.6e")

    return records


def plot_fR(f, R):
    plt.title("Photoacoustic Signal")
    plt.grid(True)
    plt.xlabel("Frequency / Hz")
    plt.ylabel("Magnitude / V")
    plt.plot(f, R, "r-")


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

    path = f"{os.getcwd()}/data/frequency_sweep_data_01.dat"

    frequency_sweep(
        lockin,
        laser,
        source,
        f_start=f_start,
        f_end=f_end,
        f_step=f_step,
        amplitude=amplitude,
        path=path,
    )
