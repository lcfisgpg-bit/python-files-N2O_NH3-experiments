# test_turn_on_lasers.py

import time
from gpg_devices_v04 import Thorlabs_ITC4002QCL

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

    

if __name__ == "__main__":
    print("Connecting the lasers source...")
    laserNH3 = Thorlabs_ITC4002QCL("USB0::0x1313::0x804A::M00884527::INSTR")
    laserN2O = Thorlabs_ITC4002QCL("USB0::0x1313::0x804A::M00977996::INSTR")
    
    print("Starting ramp_lasers...")
    ramp_lasers(laserNH3, laserN2O)
