# %%
import time
import yaml

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from drawnow import drawnow
from gpg_devices_v01 import Standford_SR830, Thorlabs_ITC4002QCL, Rigol_DG832


# %%
def frequency_sweep(
    lockin, laser, source, f_start, f_end, f_step, amplitude=80e-3, path=None, channel=1
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

    # source.set_offset(509.6e-3)
    source.set_amplitude(amplitude, channel=channel)
    source.set_frequency(f_start, channel=channel)

    for f in np.arange(f_start, f_end + f_step, f_step):
        source.set_frequency(f, channel=channel)
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

    return records


def plot_fR(f, R):
    plt.title("Photoacoustic Signal")
    plt.grid(True)
    plt.xlabel("Frequency / Hz")
    plt.ylabel("Magnitude / V")
    plt.plot(f, R, "r-")


if __name__ == "__main__":
    settings = {
        "name": "frequency_sweep_SV_v02",
        "f_start": 1000,
        "f_end": 15000,
        "f_step": 10.0,
        "offset": 509.6e-3,
        "amplitude": 80e-3,
        "waveform": "SINusoid",  # 'RAMP' for triangular waveform.
    }

    # open communication with devices
    lockin = Standford_SR830()
    laser = Thorlabs_ITC4002QCL(
        resource_name="USB0::0x1313::0x804A::M00977996::INSTR"
    )  # N2O
    source = Rigol_DG832()
    source.set_waveform(settings["waveform"])

    # start the measurement
    date_time = time.strftime(
        "%Y-%m-%d_%H-%M"
    )  # time stamp when the measurement is started
    measurement = frequency_sweep(
        lockin,
        laser,
        source,
        f_start=settings["f_start"],
        f_end=settings["f_end"],
        f_step=settings["f_step"],
        offset=settings["offset"],
        amplitude=settings["amplitude"],
        channel=1,
    )

    # save measurement data and settings to CSV and YAML files
    filename = f"./measurements/{date_time}_{settings['name']}_settings.yml"
    with open(filename, "w") as outfile:
        yaml.dump(settings, outfile)

    filename = f"./measurements/{date_time}_{settings['name']}_measurement.csv"
    df = pd.DataFrame(measurement)
    df.set_index("f", inplace=True)
    df.to_csv(
        filename,
        header=True,
        sep=",",
        float_format="%.6e",
    )
