# %%
import time
import yaml

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from drawnow import drawnow
from gpg_devices_v02 import Standford_SR830, Thorlabs_ITC4002QCL, Rigol_DG832


plt.ion()

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
    laser.set_temp(20.0)  # Set the laser temperature to 20 degrees Celsius

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




def long_term_measurement(lockin, laser, n=3600, channel=1) -> dict:
    """
    Perform a frequency sweep by adjusting the frequency of the source and recording data from the lock-in amplifier and laser temperature source.

    Parameters:
        lockin (Lockin): An instance of the Lockin class for reading lock-in amplifier data.
        laser (Laser): An instance of the Laser class for reading laser temperature data.
        time_duration (float): The duration of the long-term measurement in seconds.
        channel (int): The channel number for the signal.
    Returns:
        dict: A dictionary containing recorded data with keys 'X', 'Y', 'R', 'phase', 'f', and 't'.
    """
    
    plt.cla()
    records = {"X": [], "Y": [], "R": [], "phase": [], "f": [], "t": [], "time": []}

    t = time.time()

    for _ in range(int(n)):
        time.sleep(1)

        lockin.read()
        laser.read_temp()

        records["X"].append(lockin.X)
        records["Y"].append(lockin.Y)
        records["R"].append(lockin.R)
        records["phase"].append(lockin.phase)
        records['f'].append(lockin.f)
        # records["f"].append(f)
        records["t"].append(laser.t)
        records["time"].append(time.time() - t)

        drawnow(lambda: plot_fR(f=records["time"], R=records["R"], phase=records["phase"]))
        plt.pause(0.001)

    return records


def plot_fR(f, R, phase):
    plt.subplot(2, 1, 1)
    plt.title("Photoacoustic Signal")
    plt.grid(True)
    plt.xlabel("Frequency / Hz")
    plt.ylabel("Magnitude / V")
    plt.plot(f, R, "r-")

    plt.subplot(2, 1, 2)
    plt.title("Phase")
    plt.grid(True)
    plt.xlabel("Frequency / Hz")
    plt.ylabel("Phase / °")
    plt.plot(f, phase, "r-")


if __name__ == "__main__":
    settings = {
        "name": "long_term_stability_NH3_v01",
        "laser_current": 520e-3 , # 293.6e-3 for N2O and 520e-3 for NH3 in A
        "amplitude": 84e-3, # in V for N2O and NH3
        "waveform": "SINusoid",  # 'RAMP' for triangular waveform.
        "n": 10800, # Sample
        "laser_temperature": 46.500, # 25.0 or 41.560 N2O and 30.866 H2O and 46.500 for NH3 in Celsius
        "frequency": 1.95e3, # in Hz
        "flow": "50ccm",
    }
    channel = 1

    # open communication with devices
    lockin = Standford_SR830()
    # laser = Thorlabs_ITC4002QCL(
        #resource_name="USB0::0x1313::0x804A::M00977996::INSTR"
    #)  # N2O
    laser = Thorlabs_ITC4002QCL(
        resource_name="USB0::0x1313::0x804A::M00884527::INSTR"
    )  # NH3
    source = Rigol_DG832()

    source.set_waveform(settings["waveform"], channel = channel)
    source.set_amplitude(settings["amplitude"], channel = channel)
    source.set_frequency(settings["frequency"], channel = channel)
    
    laser.set_temp(settings["laser_temperature"])  # Set the laser temperature
    laser.set_ext_modulation(True)  # Enable external modulation for the laser
    laser.set_laser_current(settings["laser_current"])  # Set the laser current to 0.5 A

    # start the measurement
    date_time = time.strftime("%Y-%m-%d_%H-%M")  # time stamp when the measurement is started
    measurement = long_term_measurement(
        lockin,
        laser,
        n=settings["n"],
    )

    # save measurement data and settings to CSV and YAML files
    filename = f"./measurements/{date_time}_{settings['name']}_settings.yml"
    with open(filename, "w") as outfile:
        yaml.dump(settings, outfile)

    filename = f"./measurements/{date_time}_{settings['name']}_measurement.csv"
    df = pd.DataFrame(measurement)
    # df.set_index("f", inplace=True)
    df.set_index("time", inplace=True)
    df.to_csv(
        filename,
        header=True,
        sep=",",
        float_format="%.6e",
    )
