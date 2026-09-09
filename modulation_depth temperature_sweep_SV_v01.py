# %%
import time
import yaml

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from drawnow import drawnow
from gpg_devices_v03 import Standford_SR830, Thorlabs_ITC4002QCL, Rigol_DG832

plt.ion()

# %%
def temperature_sweep(lockin, laser, t_start, t_end, t_step) -> dict:
    """
    Perform a temperature sweep by adjusting the temperature of the laser and recording data from the lock-in amplifier and laser temperature source.

    Parameters:
        lockin (Lockin): An instance of the Lockin class for reading lock-in amplifier data.
        laser (Laser): An instance of the Laser class for reading laser temperature data.
        t_start (float): The starting temperature for the sweep.
        t_end (float): The ending temperature for the sweep.
        t_step (float): The temperature step size for the sweep.
        path (str): The file path for saving the recorded data.
    Returns:
        dict: A dictionary containing recorded data with keys 'X', 'Y', 'R', 'phase', 'f', and 't'.
    """
    plt.cla()
    records = {"X": [], "Y": [], "R": [], "phase": [], "f": [], "t": []}

    for t in np.arange(t_start, t_end + t_step, t_step):
        laser.set_temp(t)
        time.sleep(2.1)

        lockin.measure()
        laser.measure_temp()

        records["X"].append(lockin.X)
        records["Y"].append(lockin.Y)
        records["R"].append(lockin.R)
        records["phase"].append(lockin.phase)
        records["f"].append(lockin.f)
        records["t"].append(laser.t)

        drawnow(lambda: plot_tR_phase(t=records["t"], R=records["R"], phase=records["phase"]))
        plt.pause(0.001)

    return records


def plot_tR_phase(t, R):
    plt.title("Photoacoustic Signal")
    plt.grid(True)
    plt.xlabel("Temperature / °C")
    plt.ylabel("Magnitude / V")
    plt.plot(t, R, "r-")

def plot_tR_phase(t, R, phase):
    plt.grid(True)
    plt.subplot(2, 1, 1)

    plt.plot(t, R, "r-", label="Magnitude (R)")
    plt.title("Photoacoustic Signal")
    plt.xlabel("Temperature / °C")
    plt.ylabel("Magnitude / V")
    

    plt.subplot(2, 1, 2)
    plt.plot(t, phase, "b-", label="Phase")
    plt.title("Phase")
    plt.xlabel("Temperature / °C")
    plt.ylabel("Phase / degrees")


if __name__ == "__main__":
    settings = {
        "name": "temperature_sweep_sin_2f_140flow_nh3",
        "target gases": "NH3",
        "t_start": 42.5,  # in Celsius, 15 N2O, 20 NH3
        "t_end": 50,  # in Celsius, 45 N2O, 50 NH3
        "t_step": 0.1,  # in Celsius
        "laser_current": 520e-3,  # in A,  293e-3 N2O, 520.6e-3 NH3
        # "amplitude": 84e-3,  # in V, 84e-3 N2O, 84e-3 NH3
        "amplitude_start": 30e-3,  # in V
        "amplitude_end": 100e-3,  # in V
        "amplitude_step": 2e-3,  # in V
        "waveform": "SINusoid",  # 'RAMP' for triangular waveform.
        "frequency": 1950,  # in Hz, 1950 for 2f, 3900 for 1f
        "flow": "140ccm",
        "harmonic": 2,  # 1 for fundamental, 2 for second harmonic
    }
    channel = 1  # channel 1 for NH3, channel 2 for N2O

    # open communication with devices
    lockin = Standford_SR830()
    source = Rigol_DG832()
    #laser = Thorlabs_ITC4002QCL(resource_name="USB0::0x1313::0x804A::M00977996::INSTR")  # N2O
    laser = Thorlabs_ITC4002QCL(resource_name="USB0::0x1313::0x804A::M00884527::INSTR")  # NH3   

    # setup measurement settings
    lockin.set_harmonic(settings["harmonic"])  # Set the harmonic for the lock-in amplifier

    source.set_waveform(settings["waveform"], channel=channel)
    source.set_amplitude(settings["amplitude_start"], channel=channel)
    source.set_frequency(settings["frequency"], channel=channel)
    source.set_frequency(settings["frequency"], channel=1)

    laser.set_temp(settings["t_start"])  # Set the laser temperature
    laser.set_ext_modulation(True)  # Enable external modulation for the laser
    laser.set_laser_current(settings["laser_current"])  # Set the laser current

    # start the measurement
    date_time = time.strftime("%Y-%m-%d_%H-%M") # time stamp when the measurement is started

    for amplitude in np.arange(
        settings["amplitude_start"], settings["amplitude_end"] + settings["amplitude_step"], settings["amplitude_step"]
    ):
        # start the measurement for each amplitude
        source.set_amplitude(amplitude, channel=channel)
        time.sleep(1.0)  # wait for the amplitude to stabilize
        measurement = temperature_sweep(
            lockin,
            laser,
            t_start=settings["t_start"],
            t_end=settings["t_end"],
            t_step=settings["t_step"],
        )

        # bring the temperature back to the starting point after each sweep
        for t in np.flip(np.arange(settings["t_start"], settings["t_end"] + settings["t_step"], settings["t_step"])):
            laser.set_temp(t)
            time.sleep(0.5)  # wait for the temperature to stabilize
        time.sleep(10.0)

        # save measurement data to CSV file
        filename = f"./measurements/{date_time}_{settings['name']}_measurement{1e3*amplitude:.0f}mV.csv"
        df = pd.DataFrame(measurement)
        df.set_index("f", inplace=True)
        df.to_csv(
            filename,
            header=True,
            sep=",",
            float_format="%.6e",
        )
    
    # save measurement settings to YAML file
    filename = f"./measurements/{date_time}_{settings['name']}_settings.yml"
    with open(filename, "w") as outfile:
        yaml.dump(settings, outfile)

